from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from lists.models import Item, List

User = get_user_model()


class ItemModelsTest(TestCase):

    def test_default_text(self):
        item = Item()
        self.assertEqual(item.text, "")

    def test_item_is_related_to_list(self):
        list_ = List.objects.create()
        item = Item()
        item.list = list_
        item.save()
        self.assertIn(item, list_.item_set.all())

    def test_cannot_save_empty_list_items(self):
        list_ = List.objects.create()
        item = Item(list=list_, text="")

        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test_duplicate_items_are_invalid(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text="test")
        with self.assertRaises(ValidationError):
            item = Item(list=list_, text="test")
            item.full_clean()

    @staticmethod
    def test_CAN_save_same_item_to_different_list():
        list1 = List.objects.create()
        list2 = List.objects.create()
        Item.objects.create(list=list1, text="test")
        item = Item.objects.create(list=list2, text="test")
        item.full_clean()  # should not raise

    def test_list_ordering(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text="Item 1")
        item2 = Item.objects.create(list=list1, text="Item 2")
        item3 = Item.objects.create(list=list1, text="Item 3")
        self.assertEqual(
            list(Item.objects.all()),
            [item1, item2, item3]
        )

    def test_string_representation(self):
        item = Item(text="some text")
        self.assertEqual(str(item), "some text")


class ListModeTest(TestCase):

    def test_get_absolute_url(self):
        list_ = List.objects.create()
        self.assertEqual(list_.get_absolute_url(), f"/lists/{list_.id}/")

    def test_has_shared_with_add(self):
        user = User.objects.create(email="a@b.com")
        list_ = List.objects.create()
        get_user = User.objects.get(email="a@b.com")
        list_.shared_with.add(get_user)

        self.assertIn(user, list_.shared_with.all())

    def test_create_new_creates_list_and_first_item(self):
        List.create_new(first_item_text="new item text")
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "new item text")
        new_list = List.objects.first()
        self.assertEqual(new_item.list, new_list)

    def test_create_new_optionally_saves_owner(self):
        user = User.objects.create()
        List.create_new(first_item_text="new item text", owner=user)
        new_list = List.objects.first()
        self.assertEqual(new_list.owner, user)

    @staticmethod
    def test_lists_can_have_owners():
        List(owner=User())  # should not raise

    @staticmethod
    def test_list_owner_id_optional():
        List().full_clean()  # should not raise

    def test_list_name_is_first_item_text(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text="first item")
        Item.objects.create(list=list_, text="second item")
        self.assertEqual(list_.name, "first item")
