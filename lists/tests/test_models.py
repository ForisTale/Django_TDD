from django.test import TestCase
from django.core.exceptions import ValidationError
from lists.models import Item, List
from django.contrib.auth import get_user_model

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

    def test_lists_can_have_owners(self):
        user = User.objects.create(email="a@b.com")
        list_ = List.objects.create(owner=user)
        self.assertIn(list_, user.list_set.all())
