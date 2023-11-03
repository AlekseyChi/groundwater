import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase

from ..models import (
    ChemCodes,
    DictDocOrganizations,
    DictEntities,
    DictEquipment,
    Documents,
    Entities,
    Wells,
    WellsChem,
    WellsSample,
)


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


class DocumentsTestCase(TestCase):
    """test: Documents"""

    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser")
        self.entity = Entities.objects.create(name="entity")
        self.dict_entity = DictEntities.objects.create(name="dict entity", entity=self.entity)
        self.creation_date = datetime.date(1960, 1, 1)

    def test_create_new_document_with_required_fields(self):
        """
        Tests that the name attribute of an instance of Documents can be create with required filds.
        """
        name = "Test Document"
        typo = self.dict_entity
        time = self.creation_date

        # Create the document
        document = Documents.objects.create(
            name=name,
            typo=typo,
            creation_date=time,
        )

        # Assert that the document was created successfully
        self.assertEqual(document.name, name)
        self.assertEqual(document.typo, typo)
        self.assertEqual(document.creation_date, time)

    def test_documents_db_table(self):
        """
        Tests that correct name of the table in the database.
        """
        self.assertEqual(Documents._meta.db_table, "documents")


# WellsSample создание без/с WellsChem (может быть несколько)
# сделать тест через транзакции
class WellsSampleTestCase(TestCase):
    """test: WellsSample"""

    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser")
        self.entity = Entities.objects.create(name="entity")
        self.dict_entity = DictEntities.objects.create(name="dict entity", entity=self.entity)
        self.well = Wells.objects.create(typo=self.dict_entity)

    def test_create_new_wellssample_with_one_wellschem(self):
        """
        Tests that the create WellsSample with one WellsChem
        """
        well = self.well
        date = datetime.date(1960, 1, 1)
        name = "Test name"

        # Create the document
        wellssample = WellsSample.objects.create(
            well=well,
            date=date,
            name=name,
        )

        parameter_1 = ChemCodes.objects.create(chem_id=1, chem_name="1")
        wellschem_1 = WellsChem.objects.create(parameter=parameter_1, content_object=wellssample)
        print(wellschem_1)

        # Assert that the document was created successfully
        self.assertEqual(wellssample.well, well)
        self.assertEqual(wellssample.date, date)
        self.assertEqual(wellssample.name, name)
        self.assertEqual(wellssample.chemvalues.count(), 1)

    def test_create_new_wellssample_with_any_wellschem(self):
        """
        Tests that the create WellsSample with any WellsChem
        """
        well = self.well
        date = datetime.date(1960, 1, 1)
        name = "Test name"

        # Create the document
        wellssample = WellsSample(
            well=well,
            date=date,
            name=name,
        )

        with transaction.atomic():
            wellssample.save()

        parameter_1 = ChemCodes(chem_id=1, chem_name="схема 1")
        wellschem_1 = WellsChem(parameter=parameter_1, content_object=wellssample)

        parameter_2 = ChemCodes(chem_id=2, chem_name="схема 2")
        wellschem_2 = WellsChem(parameter=parameter_2, content_object=wellssample)

        with transaction.atomic():
            parameter_1.save()
            parameter_2.save()
            wellschem_1.save()
            wellschem_2.save()

        # Assert that the document was created successfully
        self.assertEqual(wellssample.well, well)
        self.assertEqual(wellssample.date, date)
        self.assertEqual(wellssample.name, name)
        self.assertEqual(wellssample.chemvalues.count(), 2)

    def test_wellssample_db_table(self):
        """
        Tests that correct name of the table in the database.
        """
        self.assertEqual(WellsSample._meta.db_table, "wells_sample")
