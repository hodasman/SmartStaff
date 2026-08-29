"""Переносит стартовые данные (SQLite и медиа) на постоянный том.

На платформах типа Railway диск контейнера эфемерный, поэтому БД и медиа
размещаются на примонтированном томе (пути задают переменные SQLITE_PATH и
MEDIA_ROOT). Команда запускается при старте контейнера ДО migrate и один раз
копирует файлы из репозитория на том. Существующие файлы не перезаписываются.
"""
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Копирует стартовые db.sqlite3 и media/ на постоянный том (если их там ещё нет)"

    def handle(self, *args, **options):
        self._seed_sqlite()
        self._seed_media()

    def _seed_sqlite(self):
        src = Path(settings.BASE_DIR) / "db.sqlite3"
        dst = Path(str(settings.DATABASES["default"]["NAME"]))
        if dst == src:
            return
        if dst.exists():
            self.stdout.write(f"БД уже есть на томе: {dst} - пропускаем")
            return
        if not src.exists():
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        self.stdout.write(self.style.SUCCESS(f"БД скопирована на том: {dst}"))

    def _seed_media(self):
        src_root = Path(settings.BASE_DIR) / "media"
        dst_root = Path(str(settings.MEDIA_ROOT))
        if not src_root.exists() or dst_root == src_root:
            return
        copied = 0
        for src in src_root.rglob("*"):
            if not src.is_file():
                continue
            dst = dst_root / src.relative_to(src_root)
            if dst.exists():
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
        self.stdout.write(self.style.SUCCESS(f"Медиафайлов скопировано на том: {copied}"))
