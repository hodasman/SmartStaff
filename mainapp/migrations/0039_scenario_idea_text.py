from django.db import migrations, models


def copy_idea_descriptions(apps, schema_editor):
    Scenario = apps.get_model("mainapp", "Scenario")
    database = schema_editor.connection.alias

    scenarios = (
        Scenario._base_manager.using(database)
        .select_related("idea")
        .all()
    )
    for scenario in scenarios.iterator():
        old_idea = scenario.idea
        if old_idea is None:
            continue
        scenario.idea_content = old_idea.description or old_idea.title or ""
        scenario.save(using=database, update_fields=["idea_content"])


def restore_idea_relations(apps, schema_editor):
    Idea = apps.get_model("mainapp", "Idea")
    Scenario = apps.get_model("mainapp", "Scenario")
    database = schema_editor.connection.alias

    for scenario in Scenario._base_manager.using(database).all().iterator():
        idea_content = scenario.idea_content or ""
        if not idea_content:
            continue
        idea = Idea.objects.using(database).create(
            title=scenario.title[:256],
            description=idea_content,
        )
        scenario.idea_id = idea.pk
        scenario.save(using=database, update_fields=["idea"])


class Migration(migrations.Migration):
    dependencies = [
        ("mainapp", "0038_update_platform_descriptions"),
    ]

    operations = [
        migrations.AddField(
            model_name="scenario",
            name="idea_content",
            field=models.TextField(blank=True, default="", verbose_name="Idea"),
            preserve_default=False,
        ),
        migrations.RunPython(
            copy_idea_descriptions,
            restore_idea_relations,
        ),
        migrations.RemoveField(
            model_name="scenario",
            name="idea",
        ),
        migrations.RenameField(
            model_name="scenario",
            old_name="idea_content",
            new_name="idea",
        ),
        migrations.AlterField(
            model_name="scenario",
            name="text",
            field=models.TextField(blank=True, verbose_name="Implementation"),
        ),
        migrations.AlterField(
            model_name="scenario",
            name="description",
            field=models.TextField(blank=True, verbose_name="Brief description"),
        ),
        migrations.DeleteModel(
            name="Idea",
        ),
    ]
