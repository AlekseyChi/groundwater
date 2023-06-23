# from django.core.files.storage import default_storage
# from django.core.management.base import BaseCommand

# class Command(BaseCommand):
#     help = "Tests write permissions for media directory"

#     def handle(self, *args, **options):
#         file_name = "test.txt"
#         file_content = "This is a test file."

#         if default_storage.exists(file_name):
#             self.stdout.write(self.style.WARNING(f"File {file_name} already exists"))
#         else:
#             default_storage.save(file_name, ContentFile(file_content))
#             self.stdout.write(self.style.SUCCESS(f"Successfully written to {file_name}"))
