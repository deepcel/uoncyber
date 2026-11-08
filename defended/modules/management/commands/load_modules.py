from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from accounts.models import User
from modules.content_loader import ContentError, conflicts, load, parse_directory

DEFAULT_DIR = Path(settings.BASE_DIR) / 'content' / 'modules'


class Command(BaseCommand):
    help = (
        'Create or update training modules, their sections and quizzes from the Markdown files in '
        'content/modules/. Safe to run again after editing the files. See content/README.md.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--dir', default=str(DEFAULT_DIR), help=f'Folder of module .md files (default: {DEFAULT_DIR})')
        parser.add_argument('--owner', help='Username that owns new modules (default: the first admin)')
        parser.add_argument('--draft', action='store_true', help='Load as DRAFT instead of PUBLISHED')
        parser.add_argument('--dry-run', action='store_true', help='Only check the files; change nothing')
        parser.add_argument('--force', action='store_true',
                            help='Overwrite existing modules with the same slug that were not created by this command')

    def handle(self, *args, **options):
        try:
            modules, pathway = parse_directory(options['dir'])
        except ContentError as exc:
            raise CommandError(str(exc))

        if options['dry_run']:
            for m in modules:
                self.stdout.write(
                    f'ok  {m.path.name}: "{m.fields["title"]}", {len(m.sections)} sections, {len(m.questions)} questions'
                )
            if pathway:
                self.stdout.write(f'ok  pathway "{pathway["name"]}" with {len(modules)} modules')
            for module in conflicts(modules):
                self.stdout.write(self.style.WARNING(
                    f'warning: "{module.title}" (slug {module.slug}) already exists and was not created by '
                    'load_modules; a real run needs --force to overwrite it.'
                ))
            self.stdout.write(self.style.SUCCESS('All files are valid. Nothing was changed (dry run).'))
            return

        owner = self._owner(options['owner'])

        try:
            lines = load(modules, pathway, owner, publish=not options['draft'], force=options['force'])
        except ContentError as exc:
            raise CommandError(str(exc))

        for line in lines:
            self.stdout.write(line)

        self.stdout.write(self.style.SUCCESS(
            f'Loaded {len(modules)} module(s) as {"DRAFT" if options["draft"] else "PUBLISHED"}, owned by {owner.username}.'
        ))

    def _owner(self, username):
        if username:
            user = User.objects.filter(username=username).first()
            if user is None:
                raise CommandError(f'No user called "{username}".')
            return user

        user = User.objects.filter(Q(role='ADMIN') | Q(is_superuser=True)).order_by('id').first()
        if user is None:
            raise CommandError(
                'No admin user to own the modules. Create one with "python manage.py createsuperuser", '
                'or pass --owner <username>.'
            )
        return user
