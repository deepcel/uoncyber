# from django.contrib import admin
# from .models import *

# admin.site.register(Module)
# admin.site.register(Section)
# admin.site.register(Pathway)
# admin.site.register(PathwayModule)
# admin.site.register(Enrollment)
# admin.site.register(SectionProgress)
# admin.site.register(ModuleSchedule)



from django.contrib import admin

from .models import (
    Module,
    Section,
    Pathway,
    PathwayModule,
    Enrollment,
    SectionProgress,
    ModuleSchedule,
)


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1


class ModuleScheduleInline(admin.StackedInline):
    model = ModuleSchedule
    extra = 0
    max_num = 1


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):

    list_display = ('title', 'status', 'category', 'created_by', 'pass_mark', 'updated_at')

    list_filter = ('status', 'category')

    search_fields = ('title', 'summary', 'description')

    prepopulated_fields = {'slug': ('title',)}

    inlines = [SectionInline, ModuleScheduleInline]


class PathwayModuleInline(admin.TabularInline):
    model = PathwayModule
    extra = 1


@admin.register(Pathway)
class PathwayAdmin(admin.ModelAdmin):

    list_display = ('name', 'owner', 'created_at')

    search_fields = ('name', 'description')

    inlines = [PathwayModuleInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = ('user', 'module', 'source', 'enrolled_at', 'due_at', 'last_passed_at')

    list_filter = ('source', 'module')

    search_fields = ('user__username', 'module__title')


@admin.register(SectionProgress)
class SectionProgressAdmin(admin.ModelAdmin):

    list_display = ('user', 'section', 'completed_at')

    search_fields = ('user__username', 'section__title')