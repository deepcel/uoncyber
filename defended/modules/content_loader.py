"""
Load training modules from Markdown files into the database.

Each module is one .md file (see content/README.md for the full format):

    ---
    title: Introduction to Cyber Security
    slug: introduction-to-cyber-security
    category: Fundamentals
    summary: One line shown on the module card.
    pass_mark: 80
    estimated_minutes: 45
    ---

    Module description (plain text, shown on the module page).

    ## 1.1 First section title
    Section body in Markdown...

    ## 1.2 Second section title
    ...

    # Knowledge check

    ### Question text?
    - [ ] Wrong choice
    - [x] Right choice
    Explanation: Optional, shown after the attempt.

Loading is repeatable: running it again updates modules in place (matched by slug), keeps learners'
section progress where sections still exist, and never deletes quiz questions that appear in past
attempts (they are deactivated instead, so old results stay intact).
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from django.db import transaction

from audit_log.models import AuditLog
from quizzes.models import AttemptAnswer, Choice, Question

from .models import Module, Pathway, PathwayModule, Section


class ContentError(Exception):
    """A content file is malformed. The message names the file and line."""


# Front-matter keys and how to convert them. Anything else in the front matter is an error,
# so a typo like "pass_marks" doesn't silently do nothing.
MODULE_FIELDS = {
    'title': str,
    'slug': str,
    'category': str,
    'summary': str,
    'pass_mark': int,
    'estimated_minutes': int,
    'max_attempts': int,
    'time_limit_minutes': int,
    'questions_per_attempt': int,
    'shuffle_questions': lambda v: v.strip().lower() in ('true', 'yes', '1'),
    'self_enroll_allowed': lambda v: v.strip().lower() in ('true', 'yes', '1'),
}
REQUIRED_FIELDS = ('title', 'slug', 'category')

PATHWAY_FILE = 'pathway.md'

QUIZ_HEADING = re.compile(r'^#\s+(quiz|knowledge check)\s*$', re.IGNORECASE)
SECTION_HEADING = re.compile(r'^##\s+(.+?)\s*$')
QUESTION_HEADING = re.compile(r'^###\s+(.+?)\s*$')
CHOICE_LINE = re.compile(r'^[-*]\s+\[( |x|X)\]\s+(.+?)\s*$')
EXPLANATION_LINE = re.compile(r'^explanation:\s*(.*)$', re.IGNORECASE)
POINTS_LINE = re.compile(r'^points:\s*(\d+)\s*$', re.IGNORECASE)
COMMENT = re.compile(r'<!--.*?-->', re.DOTALL)


@dataclass
class ParsedQuestion:
    text: str
    choices: list = field(default_factory=list)   # [(text, is_correct), ...]
    explanation: str = ''
    points: int = 1
    line: int = 0

    @property
    def question_type(self):
        return 'MULTIPLE' if sum(1 for _, correct in self.choices if correct) > 1 else 'SINGLE'


@dataclass
class ParsedModule:
    path: Path
    fields: dict
    description: str
    sections: list            # [(title, body), ...]
    questions: list           # [ParsedQuestion, ...]


# ---------------------------------------------------------------------------- parsing

def _front_matter(lines, path):
    """Split '---' key: value '---' off the top. Returns (dict, remaining lines, first body line number)."""
    if not lines or lines[0].strip() != '---':
        raise ContentError(f'{path.name}: must start with a "---" front-matter block.')

    for end in range(1, len(lines)):
        if lines[end].strip() == '---':
            break
    else:
        raise ContentError(f'{path.name}: front matter is missing its closing "---".')

    values = {}
    for number, raw in enumerate(lines[1:end], start=2):
        if not raw.strip():
            continue
        key, sep, value = raw.partition(':')
        if not sep:
            raise ContentError(f'{path.name}:{number}: expected "key: value", got "{raw.strip()}".')
        values[key.strip().lower()] = value.strip()

    return values, lines[end + 1:], end + 2


def _module_fields(raw, path):
    unknown = set(raw) - set(MODULE_FIELDS)
    if unknown:
        raise ContentError(f'{path.name}: unknown front-matter key(s): {", ".join(sorted(unknown))}.')

    missing = [key for key in REQUIRED_FIELDS if not raw.get(key)]
    if missing:
        raise ContentError(f'{path.name}: front matter needs {", ".join(missing)}.')

    fields = {}
    for key, value in raw.items():
        try:
            fields[key] = MODULE_FIELDS[key](value)
        except ValueError:
            raise ContentError(f'{path.name}: "{key}" must be a number, got "{value}".')

    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', fields['slug']):
        raise ContentError(f'{path.name}: slug must be lowercase words joined by hyphens, got "{fields["slug"]}".')

    return fields


def _parse_quiz(lines, first_line, path):
    questions = []
    current = None

    for offset, raw in enumerate(lines):
        number = first_line + offset
        line = raw.strip()
        if not line:
            continue

        if match := QUESTION_HEADING.match(line):
            current = ParsedQuestion(text=match.group(1), line=number)
            questions.append(current)
            continue

        if current is None:
            raise ContentError(f'{path.name}:{number}: quiz content must start with a "### Question" heading.')

        if match := CHOICE_LINE.match(line):
            current.choices.append((match.group(2), match.group(1).lower() == 'x'))
        elif match := EXPLANATION_LINE.match(line):
            current.explanation = match.group(1)
        elif match := POINTS_LINE.match(line):
            current.points = int(match.group(1))
        elif current.explanation:
            current.explanation += ' ' + line          # explanation continued on the next line
        else:
            raise ContentError(
                f'{path.name}:{number}: expected "- [ ] choice", "- [x] choice" or "Explanation: ...", got "{line}".'
            )

    for q in questions:
        if len(q.choices) < 2:
            raise ContentError(f'{path.name}:{q.line}: "{q.text}" needs at least two choices.')
        if not any(correct for _, correct in q.choices):
            raise ContentError(f'{path.name}:{q.line}: "{q.text}" has no correct choice marked with [x].')
        if any(len(text) > 500 for text, _ in q.choices):
            raise ContentError(f'{path.name}:{q.line}: a choice is longer than 500 characters.')

    return questions


def parse_module(path):
    """Parse one module file. Raises ContentError with the file and line on any problem."""
    path = Path(path)
    text = COMMENT.sub('', path.read_text(encoding='utf-8'))   # <!-- reviewer notes --> never reach the database
    lines = text.splitlines()

    raw_fields, body, first_line = _front_matter(lines, path)
    fields = _module_fields(raw_fields, path)

    description, sections, quiz_start = [], [], None
    current = None
    in_fence = False

    for offset, raw in enumerate(body):
        if raw.lstrip().startswith('```'):
            in_fence = not in_fence

        if not in_fence:
            if QUIZ_HEADING.match(raw.strip()):
                quiz_start = offset
                break
            if match := SECTION_HEADING.match(raw):
                current = [match.group(1), []]
                sections.append(current)
                continue

        (current[1] if current else description).append(raw)

    if not sections:
        raise ContentError(f'{path.name}: no sections found. Start each section with "## Title".')

    questions = []
    if quiz_start is not None:
        questions = _parse_quiz(body[quiz_start + 1:], first_line + quiz_start + 1, path)

    return ParsedModule(
        path=path,
        fields=fields,
        description='\n'.join(description).strip(),
        sections=[(title, '\n'.join(lines).strip()) for title, lines in sections],
        questions=questions,
    )


def parse_pathway(path):
    """pathway.md: front matter with name and description. Modules join it in file-name order."""
    path = Path(path)
    raw, _, _ = _front_matter(COMMENT.sub('', path.read_text(encoding='utf-8')).splitlines(), path)
    if not raw.get('name'):
        raise ContentError(f'{path.name}: front matter needs "name".')
    return {'name': raw['name'], 'description': raw.get('description', '')}


def parse_directory(directory):
    """All module files (sorted by file name, so prefix them 01-, 02-, ...) plus the optional pathway."""
    directory = Path(directory)
    if not directory.is_dir():
        raise ContentError(f'Content folder not found: {directory}')

    files = sorted(p for p in directory.glob('*.md') if p.name.lower() not in (PATHWAY_FILE, 'readme.md'))
    if not files:
        raise ContentError(f'No module files (*.md) in {directory}')

    modules = [parse_module(p) for p in files]

    slugs = [m.fields['slug'] for m in modules]
    duplicates = {s for s in slugs if slugs.count(s) > 1}
    if duplicates:
        raise ContentError(f'Two files use the same slug: {", ".join(sorted(duplicates))}')

    pathway_file = directory / PATHWAY_FILE
    pathway = parse_pathway(pathway_file) if pathway_file.exists() else None

    return modules, pathway


# ---------------------------------------------------------------------------- saving

def _sync_sections(module, parsed_sections):
    existing = list(module.sections.order_by('order', 'id'))
    created = updated = 0

    # Match by position, so learners keep progress on sections that are only reworded.
    for index, (title, body) in enumerate(parsed_sections):
        order = index + 1
        if index < len(existing):
            section = existing[index]
            if (section.title, section.body, section.order) != (title, body, order):
                section.title, section.body, section.order = title, body, order
                section.save(update_fields=['title', 'body', 'order'])
                updated += 1
        else:
            Section.objects.create(module=module, title=title, body=body, order=order)
            created += 1

    removed = len(existing[len(parsed_sections):])
    for section in existing[len(parsed_sections):]:
        section.delete()

    return created, updated, removed


def _same_question(question, parsed):
    choices = [(c.text, c.is_correct) for c in question.choices.order_by('order', 'id')]
    return (
        question.text == parsed.text
        and question.question_type == parsed.question_type
        and question.explanation == parsed.explanation
        and question.points == parsed.points
        and choices == parsed.choices
    )


def _create_question(module, parsed, order):
    question = Question.objects.create(
        module=module, text=parsed.text, question_type=parsed.question_type,
        explanation=parsed.explanation, points=parsed.points, order=order,
    )
    Choice.objects.bulk_create([
        Choice(question=question, text=text, is_correct=correct, order=i + 1)
        for i, (text, correct) in enumerate(parsed.choices)
    ])


def _retire(question):
    """Delete a question, or deactivate it if learners' past results refer to it."""
    if AttemptAnswer.objects.filter(question=question).exists():
        question.is_active = False
        question.save(update_fields=['is_active'])
    else:
        question.delete()


def _sync_questions(module, parsed_questions):
    existing = list(Question.objects.filter(module=module, is_active=True).order_by('order', 'id'))
    created = updated = removed = 0

    for index, parsed in enumerate(parsed_questions):
        order = index + 1
        question = existing[index] if index < len(existing) else None

        if question is not None and _same_question(question, parsed):
            if question.order != order:
                question.order = order
                question.save(update_fields=['order'])
            continue

        if question is not None:
            _retire(question)   # changed: replace it rather than rewrite answers learners already gave
            updated += 1
        else:
            created += 1
        _create_question(module, parsed, order)

    for question in existing[len(parsed_questions):]:
        _retire(question)
        removed += 1

    return created, updated, removed


LOADER_SOURCE = 'load_modules'   # audit-log marker for modules this loader created or took over


def _loader_managed_ids():
    return set(
        AuditLog.objects.filter(action='MODULE_CREATED', details__source=LOADER_SOURCE)
        .values_list('details__module_id', flat=True)
    )


def conflicts(modules):
    """
    Existing modules that share a slug with a content file but weren't created by this loader,
    e.g. a module someone built by hand in the app. Loading would overwrite their sections, so the
    command refuses unless --force is given.
    """
    managed = _loader_managed_ids()
    slugs = [m.fields['slug'] for m in modules]
    return [m for m in Module.objects.filter(slug__in=slugs).order_by('id') if m.pk not in managed]


def _mark_managed(module, owner, adopted):
    AuditLog.objects.create(
        user=owner, action='MODULE_CREATED', ip_address='127.0.0.1',   # run from the command line
        details={'module_id': module.pk, 'title': module.title, 'source': LOADER_SOURCE, 'adopted': adopted},
    )


@transaction.atomic
def load(modules, pathway, owner, publish=True, force=False):
    """
    Create or update every module (and the pathway). Returns one summary line per item.
    Raises ContentError, changing nothing, if a module would overwrite one not made by this loader,
    unless force=True (which takes the module over from then on).
    """
    clashing = conflicts(modules)
    if clashing and not force:
        names = ', '.join(f'"{m.title}" (slug {m.slug}, id {m.pk})' for m in clashing)
        raise ContentError(
            f'These modules already exist and were not created by load_modules: {names}. '
            'Loading would replace their sections. Change the slug in the content file to load '
            'alongside them, or run again with --force to overwrite them.'
        )
    adopting = {m.pk for m in clashing}
    managed = _loader_managed_ids()

    report = []
    saved = []

    for parsed in modules:
        values = {
            **parsed.fields,
            'description': parsed.description or parsed.fields.get('summary', ''),
            'status': 'PUBLISHED' if publish else 'DRAFT',
        }
        slug = values.pop('slug')

        module = Module.objects.filter(slug=slug).first()
        if module is None:
            module = Module.objects.create(slug=slug, created_by=owner, **values)
            action = 'created'
        else:
            for key, value in values.items():
                setattr(module, key, value)
            if module.created_by is None:
                module.created_by = owner
            module.save()
            action = 'replaced' if module.pk in adopting else 'updated'

        if module.pk not in managed:
            _mark_managed(module, owner, adopted=module.pk in adopting)

        s_new, s_changed, s_removed = _sync_sections(module, parsed.sections)
        q_new, q_changed, q_removed = _sync_questions(module, parsed.questions)
        saved.append(module)

        report.append(
            f'{action:8} {module.title}: {len(parsed.sections)} sections '
            f'(+{s_new} ~{s_changed} -{s_removed}), {len(parsed.questions)} questions '
            f'(+{q_new} ~{q_changed} -{q_removed})'
        )

    if pathway:
        path_obj, created = Pathway.objects.get_or_create(
            name=pathway['name'], defaults={'description': pathway['description'], 'owner': owner}
        )
        if not created and path_obj.description != pathway['description']:
            path_obj.description = pathway['description']
            path_obj.save(update_fields=['description'])

        path_obj.pathwaymodule_set.exclude(module__in=saved).delete()
        for order, module in enumerate(saved, start=1):
            PathwayModule.objects.update_or_create(pathway=path_obj, module=module, defaults={'order': order})

        report.append(f'{"created" if created else "updated":8} pathway {path_obj.name}: {len(saved)} modules')

    return report
