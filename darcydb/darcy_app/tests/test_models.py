from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import DictDocOrganizations, DictEntities, DictEquipment, Entities

# class BaseModelTestCase(TestCase):
#     """
#     test: BaseModel
#     """
#     def setUp(self):
#         # Создаем тестовые данные для модели Entities
#         self.user = get_user_model().objects.create(username='testuser')

#     def test_base_model_creation_with_default_values(self):
#         """
#         Tests that a BaseModel object can be created with default values for all fields
#         """
#         base_model = BaseModel(last_user=self.user)
#         self.assertIsNone(base_model.created)
#         self.assertIsNone(base_model.modified)
#         self.assertEqual(base_model.author, "ufo")
#         self.assertIsNotNone(base_model.last_user)
#         self.assertIsNone(base_model.remote_addr)
#         self.assertIsNone(base_model.extra)
#         self.assertIsNotNone(base_model.uuid)

#     def test_base_model_creation_with_non_default_values(self):
#         """
#         Tests that a BaseModel object can be created with non-default values for all fields
#         """
#         base_model = BaseModel(created=timezone.now(), modified=timezone.now(), author="test_author",
# last_user=self.user, remote_addr="127.0.0.1", extra={"key": "value"}, uuid=uuid.uuid4())
#         self.assertIsNotNone(base_model.created)
#         self.assertIsNotNone(base_model.modified)
#         self.assertEqual(base_model.author, "test_author")
#         self.assertIsNotNone(base_model.last_user)
#         self.assertEqual(base_model.remote_addr, "127.0.0.1")
#         self.assertEqual(base_model.extra, {"key": "value"})
#         self.assertIsNotNone(base_model.uuid)

#     def test_base_model_save_successfully(self):
#         """
#         Tests that a BaseModel object can be saved successfully
#         """
#         base_model = BaseModel()
#         base_model.save()
#         self.assertIsNotNone(base_model.pk)

#     def test_base_model_update_successfully(self):
#         """
#         Tests that a BaseModel object can be updated successfully
#         """
#         base_model = BaseModel()
#         base_model.save()
#         base_model.author = "updated_author"
#         base_model.save()
#         self.assertEqual(base_model.author, "updated_author")

#     def test_base_model_delete_successfully(self):
#         """
#         Tests that a BaseModel object can be deleted successfully
#         """
#         base_model = BaseModel()
#         base_model.save()
#         base_model.delete()
#         with self.assertRaises(BaseModel.DoesNotExist):
#             BaseModel.objects.get(pk=base_model.pk)

#     def test_base_model_creation_with_null_values(self):
#         """
#         Tests that a BaseModel object cannot be created with null values for all fields
#         """
#         with self.assertRaises(IntegrityError):
#             BaseModel.objects.create(
#                 created=None,
#                 modified=None,
#                 author=None,
#                 last_user=None,
#                 remote_addr=None,
#                 extra=None,
#                 uuid=None
#             )


class EntitiesTestCase(TestCase):
    """test: Entities"""

    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser")

    def test_create_instance_with_valid_name(self):
        """
        Tests that an instance of 'Entities' can be created with a valid name and saved successfully.
        """
        entity = Entities(name="Valid Name")
        entity.save()
        self.assertEqual(Entities.objects.count(), 1)
        self.assertEqual(Entities.objects.first().name, "Valid Name")

    def test_retrieve_instance_by_name(self):
        """
        Tests that an instance of 'Entities' can be retrieved from the database using its name.
        """
        entity = Entities(name="Valid Name")
        entity.save()
        retrieved_entity = Entities.objects.get(name="Valid Name")
        self.assertEqual(retrieved_entity.id, entity.id)

    def test_update_instance_with_valid_name(self):
        """
        Tests that an instance of 'Entities' can be updated with a new valid name and saved successfully.
        """
        entity = Entities(name="Old Name")
        entity.save()
        entity.name = "New Name"
        entity.save()
        self.assertEqual(Entities.objects.count(), 1)
        self.assertEqual(Entities.objects.first().name, "New Name")

    def test_delete_instance(self):
        """
        Tests that an instance of 'Entities' can be deleted from the database.
        """
        entity = Entities(name="Valid Name")
        entity.save()
        entity.delete()
        self.assertEqual(Entities.objects.count(), 0)

    def test_entities_db_table(self):
        """
        Tests that correct name of the table in the database.
        """
        self.assertEqual(Entities._meta.db_table, "entities")


class DictEntitiesTestCase(TestCase):
    """test: DictEntities"""

    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser")
        self.entity = Entities.objects.create(name="entity")

    def test_create_dict_entities_with_valid_fields(self):
        """
        Tests that a new DictEntities object can be created with valid name and entity fields.
        """
        dict_entity = DictEntities(name="Test Entity", entity=self.entity)
        self.assertEqual(dict_entity.name, "Test Entity")
        self.assertEqual(dict_entity.entity, self.entity)

    def test_save_dict_entities_to_database(self):
        """
        Tests that a new DictEntities object can be saved to the database.
        """
        dict_entity = DictEntities(name="Test Entity", entity=self.entity)
        dict_entity.save()
        self.assertTrue(DictEntities.objects.filter(name="Test Entity").exists())

    def test_retrieve_dict_entities_from_database(self):
        """
        Tests that an existing DictEntities object can be retrieved from the database.
        """
        dict_entity = DictEntities(name="Test Entity", entity=self.entity)
        dict_entity.save()
        retrieved_entity = DictEntities.objects.get(name="Test Entity")
        self.assertEqual(retrieved_entity.name, "Test Entity")
        self.assertEqual(retrieved_entity.entity, self.entity)

    def test_update_dict_entities_fields(self):
        """
        Tests that the name and entity fields of an existing DictEntities object can be updated.
        """
        dict_entity = DictEntities(name="Test Entity", entity=self.entity)
        update_entity = Entities.objects.create(name="Update entity")
        dict_entity.save()
        dict_entity.name = "Updated Entity"
        dict_entity.entity = update_entity
        dict_entity.save()
        updated_entity = DictEntities.objects.get(name="Updated Entity")
        self.assertEqual(updated_entity.name, "Updated Entity")
        self.assertEqual(updated_entity.entity, update_entity)

    def test_delete_dict_entities_from_database(self):
        """
        Tests that an existing DictEntities object can be deleted from the database.
        """
        dict_entity = DictEntities(name="Test Entity", entity=self.entity)
        dict_entity.save()
        dict_entity.delete()
        self.assertFalse(DictEntities.objects.filter(name="Test Entity").exists())

    def test_dict_entities_db_table(self):
        """
        Tests that correct name of the table in the database.
        """
        self.assertEqual(DictEntities._meta.db_table, "dict_entities")


class DictEquipmentTestCase(TestCase):
    """test: DictEquipment"""

    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser")
        self.entity = Entities.objects.create(name="entity")
        self.dict_entity = DictEntities.objects.create(name="dict entity", entity=self.entity)

    def test_create_dict_equipment_with_required_fields(self):
        """
        Tests that a DictEquipment instance can be created with the required fields.
        """
        dict_equipment = DictEquipment.objects.create(typo=self.dict_entity, brand="Brand")
        self.assertIsNotNone(dict_equipment)
        self.assertEqual(dict_equipment.typo, DictEntities.objects.first())
        self.assertEqual(dict_equipment.brand, "Brand")

    def test_create_dict_equipment_with_all_fields(self):
        """
        Tests that a DictEquipment instance can be created with all fields
        """
        dict_equipment = DictEquipment.objects.create(typo=self.dict_entity, name="Name", brand="Brand")
        self.assertIsNotNone(dict_equipment)
        self.assertEqual(dict_equipment.typo, DictEntities.objects.first())
        self.assertEqual(dict_equipment.name, "Name")
        self.assertEqual(dict_equipment.brand, "Brand")

    def test_update_dict_equipment(self):
        """
        Tests that a DictEquipment instance can be updated
        """
        dict_equipment = DictEquipment.objects.create(typo=self.dict_entity, brand="Brand")
        dict_equipment.brand = "New Brand"
        dict_equipment.save()
        updated_dict_equipment = DictEquipment.objects.get(id=dict_equipment.id)
        self.assertEqual(updated_dict_equipment.brand, "New Brand")

    def test_delete_dict_equipment(self):
        """
        Tests that a DictEquipment instance can be deleted
        """
        dict_equipment = DictEquipment.objects.create(typo=self.dict_entity, brand="Brand")
        dict_equipment.delete()
        with self.assertRaises(DictEquipment.DoesNotExist):
            DictEquipment.objects.get(id=dict_equipment.id)

    def test_dict_equipment_db_table(self):
        """
        Tests that correct name of the table in the database.
        """
        self.assertEqual(DictEquipment._meta.db_table, "dict_equipment")


class DictDocOrganizationsTestCase(TestCase):
    """test: DictDocOrganizations"""

    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser")
        # self.entity = Entities.objects.create(name="entity")
        # self.dict_entity = DictEntities.objects.create(name="dict entity", entity=self.entity)

    def test_instance_creation(self):
        """
        Tests that an instance of DictDocOrganizations can be created with a name attribute.
        """
        organization = DictDocOrganizations(name="Test Organization")
        self.assertEqual(organization.name, "Test Organization")

    def test_instance_saving(self):
        """
        Tests that an instance of DictDocOrganizations can be saved to the database.
        """
        organization = DictDocOrganizations(name="Test Organization")
        organization.save()
        self.assertIsNotNone(organization.pk)

    def test_instance_retrieval(self):
        """
        Tests that an instance of DictDocOrganizations can be retrieved from the database
        and the name attribute is correct.
        """
        organization = DictDocOrganizations(name="Test Organization")
        organization.save()

        retrieved_organization = DictDocOrganizations.objects.get(pk=organization.pk)
        self.assertEqual(retrieved_organization.name, "Test Organization")

    def test_instance_update(self):
        """
        Tests that the name attribute of an instance of DictDocOrganizations can be updated and saved to the database.
        """
        organization = DictDocOrganizations(name="Test Organization")
        organization.save()

        organization.name = "Updated Organization"
        organization.save()

        retrieved_organization = DictDocOrganizations.objects.get(pk=organization.pk)
        self.assertEqual(retrieved_organization.name, "Updated Organization")

    def test_dict_doc_organizations_db_table(self):
        """
        Tests that correct name of the table in the database.
        """
        self.assertEqual(DictDocOrganizations._meta.db_table, "dict_doc_organization")
