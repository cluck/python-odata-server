import json
import unittest
import xml.etree.cElementTree as ET

from odata_server.edm import DataServices, Edmx, EntitySet, EntityType, Schema

ENTITY_TYPE1 = {
    "Name": "Shipping",
    "Key": [
        {"Name": "ID"},
    ],
    "Properties": [
        {"Name": "ID", "Type": "Edm.String", "Nullable": False},
        {"Name": "emails", "Type": "Collection(Edm.String)", "Nullable": False},
        {"Name": "recipient", "Type": "Edm.String", "Nullable": False},
    ]
}

ENTITY_TYPE2 = {
    "Name": "Employee",
    "Key": [
        {"Name": "ID"},
    ],
    "Properties": [
        {"Name": "ID", "Type": "Edm.String", "Nullable": False},
        {"Name": "FirstName", "Type": "Edm.String", "Nullable": False},
        {"Name": "LastName", "Type": "Edm.String", "Nullable": False},
    ],
    "NavigationProperty": [
        {"Name": "Manager", "Type": "self.Manager"},
    ]
}

SCHEMA1 = {
    "Namespace": "Testing",
    "Alias": "t",
    "EntityTypes": [
        ENTITY_TYPE1,
        ENTITY_TYPE2,
    ]
}

ENTITY_SET1 = {
    "Name": "Products",
    "EntityType": "Product",
    "IncludeInServiceDocument": False,
    "NavigationPropertyBindings": [
        {
            "Path": "Category",
            "Target": "SomeModel.SomeContainer/Categories",
        },
    ],
    "Annotations": [
        {
            "Term": "UI.DisplayName",
            "String": "Products"
        }
    ]
}


class EdmUnitTests(unittest.TestCase):

    def test_entity_set_minimal(self):
        e = EntitySet({
            "Name": "Products",
            "EntityType": "Product"
        })

        self.assertEqual(e.Name, "Products")
        self.assertEqual(e.IncludeInServiceDocument, True)
        self.assertEqual(len(e.NavigationPropertyBindings), 0)
        self.assertEqual(len(e.Annotations), 0)

        with self.subTest(msg="JSON serialization"):
            e.json()

    def test_entity_set_full(self):
        e = EntitySet(ENTITY_SET1)

        self.assertEqual(e.Name, "Products")
        self.assertEqual(e.IncludeInServiceDocument, False)
        self.assertEqual(len(e.NavigationPropertyBindings), 1)
        self.assertEqual(len(e.Annotations), 1)

        with self.subTest(msg="JSON serialization"):
            e.json()

    def test_entity_type_minimal(self):
        e = EntityType({
            "Name": "h"
        })

        self.assertEqual(e.Name, "h")
        self.assertEqual(len(e.Properties), 0)

    def test_entity_type_full(self):
        e = EntityType(ENTITY_TYPE1)

        self.assertEqual(e.Name, "Shipping")
        self.assertEqual(len(e.Key.PropertyRefs), 1)
        self.assertEqual(e.Key.PropertyRefs[0].Name, "ID")
        self.assertEqual(len(e.Properties), 3)

    def test_schema_minimal(self):
        s = Schema({
            "Namespace": "Testing"
        })
        self.assertEqual(s.Namespace, "Testing")

    def test_schema_full(self):
        s = Schema(SCHEMA1)
        self.assertEqual(s.Namespace, "Testing")
        self.assertEqual(s.Alias, "t")
        self.assertEqual(len(s.EntityTypes), 2)

    def test_dataservices_minimal(self):
        d = DataServices([{
            "Namespace": "Testing",
        }])
        self.assertEqual(len(d.Schemas), 1)

    def test_dataservices_full(self):
        d = DataServices([
            SCHEMA1
        ])
        self.assertEqual(len(d.Schemas), 1)

    def test_dataservices_full_verbose(self):
        d = DataServices({
            "Schemas": [
                SCHEMA1
            ]
        })
        self.assertEqual(len(d.Schemas), 1)
        self.assertEqual(type(d.json()), list)

    def test_schema_key_with_alias(self):
        s = Schema({
            "Namespace": "ODataDemo",
            "EntityTypes": [
                {
                    "Name": "Category",
                    "Key": [
                        {"Name": "Info/ID", "Alias": "EntityInfoID"},
                    ],
                    "Properties": [
                        {"Name": "Info", "Type": "self.EntityInfo"},
                        {"Name": "Name", "Nullable": True},
                    ],
                },
            ],
            "EntityContainers": [
                {
                    "Name": "Container",
                }
            ],
            "ComplexTypes": [
                {
                    "Name": "EntityInfo",
                    "Properties": [
                        {"Name": "ID", "Type": "Edm.Int32"},
                        {"Name": "Created", "Type": "Edm.DateTimeOffset", "Precision": 0},
                    ],
                },
            ]
        })
        self.assertEqual(len(s.EntityTypes), 1)
        self.assertEqual(len(s.ComplexTypes), 1)
        self.assertEqual(len(s.EntityContainers), 1)
        print(json.dumps(s.json(), indent=4))

    def test_edmx(self):
        edmx = Edmx({
            "DataServices": [{
                "Namespace": "ODataDemo",
                "EntityTypes": [
                    {
                        "Name": "Product",
                        "HasStream": True,
                        "Key": [{"Name": "ID"}],
                        "Properties": [
                            {
                                "Name": "ID",
                                "Type": "Edm.Int32",
                                "Nullable": False
                            },
                            {
                                "Name": "Description",
                                "Type": "Edm.String",
                                "Annotations": [
                                    {"Term": "Core.IsLanguageDependent"},
                                ],
                            },
                        ],
                        "NavigationProperties": [
                            {
                                "Name": "Category",
                                "Partner": "Products",
                                "Type": "ODataDemo.Category",
                                "Nullable": False,
                                "Annotations": [
                                    {"Term": "PythonODataServer.Embedded", "Bool": True},
                                ],
                            }
                        ],
                    },
                    {
                        "Name": "Category",
                        "Key": [{"Name": "ID"}],
                        "Properties": [
                            {
                                "Name": "ID",
                                "Type": "Edm.Int32",
                                "Nullable": False
                            },
                            {
                                "Name": "Name",
                                "Type": "Edm.String",
                                "Nullable": False,
                                "Annotations": [
                                    {"Term": "Core.IsLanguageDependent"},
                                ]
                            },
                        ],
                        "NavigationProperties": [
                            {
                                "Name": "Products",
                                "Partner": "Category",
                                "Type": "Collection(ODataDemo.Product)",
                                "OnDelete": {"Action": "Cascade"}
                            }
                        ]
                    },
                ],
                "EntityContainers": [
                    {
                        "Name": "DemoService",
                        "EntitySets": [
                            {
                                "Name": "Products",
                                "EntityType": "ODataDemo.Product",
                                "NavigationPropertyBindings": [
                                    {
                                        "Path": "Category",
                                        "Target": "Categories"
                                    },
                                ],
                            },
                            {
                                "Name": "Categories",
                                "EntityType": "ODataDemo.Category",
                                "NavigationPropertyBindings": [{
                                    "Path": "Products",
                                    "Target": "Products"
                                }],
                            },
                        ],
                    }
                ]
            }]
        })

        ET.tostring(edmx.xml())


if __name__ == "__main__":
    unittest.main()
