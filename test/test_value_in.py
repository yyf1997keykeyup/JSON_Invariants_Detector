# coding=utf-8
import unittest
import time
from src.converter.schema_generator import SchemaGenerator
from src.record_map.record_map import RecordMap
from src.util.const import HTTPMethodKey


class TestValueIn(unittest.TestCase):
    def setUp(self):
        self.schema_generator = SchemaGenerator()
        self.record_map = RecordMap()

    def test_two_data(self):
        """
        pattern 1
        have 2 json data
        """
        data_1 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 60
            }
        }
        data_2 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 99
            }
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"name": "Yufeng"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)
        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"name": "Yinuo"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)

        self.record_map.load()

        """print to file"""
        # json_str = json.dumps(self.record_map.get_records(), indent=4)
        # print_to_file(json_str, file_name="../../output/pattern1/record.txt")

        invariant_schema = self.record_map.generate_invariant_schema()

        """print to file"""
        # json_str = json.dumps(invariant_schema, indent=4)
        # print_to_file(json_str, file_name="../../output/pattern1/invariant_schema.txt")

        target_path = invariant_schema["properties"]["data"]["possible_types"]["object"]["properties"][
            "grade"]["possible_types"]["integer"]

        assert "value_in" in target_path
        assert len(target_path["value_in"]) == 2
        assert 60 in target_path["value_in"]
        assert 99 in target_path["value_in"]

    def test_duplicated_data(self):
        """
        pattern 1
        have 3 json data
        """
        data_1 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 60
            }
        }
        data_2 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 99
            }
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"name": "Yufeng"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)

        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"name": "Yinuo"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)

        schema_3 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"name": "Tyler"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_3)

        self.record_map.load()

        """print to file"""
        # json_str = json.dumps(self.record_map.get_records(), indent=4)
        # print_to_file(json_str, file_name="../../output/pattern1/record.txt")

        invariant_schema = self.record_map.generate_invariant_schema()

        """print to file"""
        # json_str = json.dumps(invariant_schema, indent=4)
        # print_to_file(json_str, file_name="../../output/pattern1/invariant_schema.txt")

        target_path = invariant_schema["properties"]["data"]["possible_types"]["object"]["properties"][
            "grade"]["possible_types"]["integer"]

        assert len(target_path["value_in"]) == 2
        assert 60 in target_path["value_in"]
        assert 99 in target_path["value_in"]

    def test_excessive_range(self):
        """
        pattern 1
        test when the potential of value is more than param--"value_in_max"
        have 5 json data
        """
        data_1 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 60
            }
        }
        data_2 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 99
            }
        }
        data_3 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 100
            }
        }
        data_4 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 0
            }
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"name": "Yufeng"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)

        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"name": "Yinuo"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)

        schema_3 = self.schema_generator.generate(json_dict=data_3,
                                                  request_params={"name": "John"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_3)

        schema_4 = self.schema_generator.generate(json_dict=data_4,
                                                  request_params={"name": "Jason"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_4)

        self.record_map.load()

        """print to file"""
        # json_str = json.dumps(self.record_map.get_records(), indent=4)
        # print_to_file(json_str, file_name="../../output/pattern1/record.txt")

        invariant_schema = self.record_map.generate_invariant_schema(
            value_in_max=3)  # if over 3, invariant does not hold

        """print to file"""
        # json_str = json.dumps(invariant_schema, indent=4)
        # print_to_file(json_str, file_name="../../output/pattern1/invariant_schema.txt")

        target_path = invariant_schema["properties"]["data"]["possible_types"]["object"]["properties"][
            "grade"]["possible_types"]["integer"]

        assert "value_in" in target_path
        assert len(target_path["value_in"]) == 0  # means this invariant does not hold

    def test_same_monitor(self):
        """
        pattern 1
        test monitor function for the same input
        """
        data_1 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 60
            }
        }
        data_2 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 60
            }
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"name": "Yufeng"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)
        self.record_map.load()

        invariant_schema = self.record_map.generate_invariant_schema()

        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"name": "Yinuo"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)
        self.record_map.load()

        invariant_schema_changed = self.record_map.generate_invariant_schema()

        assert invariant_schema == invariant_schema_changed  # schema unchanged

    def test_diff_monitor(self):
        """
        pattern 1
        test monitor function for the different input
        """
        data_1 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 60
            }
        }
        data_2 = {
            "code": 200,
            "message": "success",
            "data": {
                "grade": 90
            }
        }

        schema_1 = self.schema_generator.generate(json_dict=data_1,
                                                  request_params={"name": "Yufeng"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_1)

        self.record_map.load()
        invariant_schema = self.record_map.generate_invariant_schema()

        schema_2 = self.schema_generator.generate(json_dict=data_2,
                                                  request_params={"name": "Yinuo"},
                                                  http_method=HTTPMethodKey.GET)
        self.record_map.add(schema_2)
        self.record_map.load()

        invariant_schema_changed = self.record_map.generate_invariant_schema()

        # todo: give diff info
        assert invariant_schema != invariant_schema_changed  # schema changed

    def test_a_lot(self):
        for grade in range(101):
            data = {
                "code": 200,
                "message": "success",
                "data": {
                    "grade": grade
                }
            }
            schema = self.schema_generator.generate(json_dict=data,
                                                    request_params={"name": chr(65 + grade)},
                                                    http_method=HTTPMethodKey.GET)
            self.record_map.add(schema)

        self.record_map.load()
        invariant_schema = self.record_map.generate_invariant_schema()
        pass

    # to test a complicated api, input it to the record table for 100,000 times.
    def test_complicated_api(self):
        for grade in range(100001):
            if grade % 1000 == 0:
                print(grade)
            data = {
                "google": {"web-app": {
                    "servlet": [
                        {
                            "servlet-name": "cofaxCDS",
                            "servlet-class": "org.cofax.cds.CDSServlet",
                            "init-param": {
                                "configGlossary:installationAt": "Philadelphia, PA",
                                "configGlossary:adminEmail": "ksm@pobox.com",
                                "configGlossary:poweredBy": "Cofax",
                                "configGlossary:poweredByIcon": "/images/cofax.gif",
                                "configGlossary:staticPath": "/content/static",
                                "templateProcessorClass": "org.cofax.WysiwygTemplate",
                                "templateLoaderClass": "org.cofax.FilesTemplateLoader",
                                "templatePath": "templates",
                                "templateOverridePath": "",
                                "defaultListTemplate": "listTemplate.htm",
                                "defaultFileTemplate": "articleTemplate.htm",
                                "useJSP": False,
                                "jspListTemplate": "listTemplate.jsp",
                                "jspFileTemplate": "articleTemplate.jsp",
                                "cachePackageTagsTrack": 200,
                                "cachePackageTagsStore": 200,
                                "cachePackageTagsRefresh": 60,
                                "cacheTemplatesTrack": 100,
                                "cacheTemplatesStore": 50,
                                "cacheTemplatesRefresh": 15,
                                "cachePagesTrack": 200,
                                "cachePagesStore": 100,
                                "cachePagesRefresh": 10,
                                "cachePagesDirtyRead": 10,
                                "searchEngineListTemplate": "forSearchEnginesList.htm",
                                "searchEngineFileTemplate": "forSearchEngines.htm",
                                "searchEngineRobotsDb": "WEB-INF/robots.db",
                                "useDataStore": True,
                                "dataStoreClass": "org.cofax.SqlDataStore",
                                "redirectionClass": "org.cofax.SqlRedirection",
                                "dataStoreName": "cofax",
                                "dataStoreDriver": "com.microsoft.jdbc.sqlserver.SQLServerDriver",
                                "dataStoreUrl": "jdbc:microsoft:sqlserver://LOCALHOST:1433;DatabaseName=goon",
                                "dataStoreUser": "sa",
                                "dataStorePassword": "dataStoreTestQuery",
                                "dataStoreTestQuery": "SET NOCOUNT ON;select test='test';",
                                "dataStoreLogFile": "/usr/local/tomcat/logs/datastore.log",
                                "dataStoreInitConns": 10,
                                "dataStoreMaxConns": 100,
                                "dataStoreConnUsageLimit": 100,
                                "dataStoreLogLevel": "debug",
                                "maxUrlLength": 500}},
                        {
                            "servlet-name": "cofaxEmail",
                            "servlet-class": "org.cofax.cds.EmailServlet",
                            "init-param": {
                                "mailHost": "mail1",
                                "mailHostOverride": "mail2"}},
                        {
                            "servlet-name": "cofaxAdmin",
                            "servlet-class": "org.cofax.cds.AdminServlet"},

                        {
                            "servlet-name": "fileServlet",
                            "servlet-class": "org.cofax.cds.FileServlet"},
                        {
                            "servlet-name": "cofaxTools",
                            "servlet-class": "org.cofax.cms.CofaxToolsServlet",
                            "init-param": {
                                "templatePath": "toolstemplates/",
                                "log": 1,
                                "logLocation": "/usr/local/tomcat/logs/CofaxTools.log",
                                "logMaxSize": "",
                                "dataLog": 1,
                                "dataLogLocation": "/usr/local/tomcat/logs/dataLog.log",
                                "dataLogMaxSize": "",
                                "removePageCache": "/content/admin/remove?cache=pages&id=",
                                "removeTemplateCache": "/content/admin/remove?cache=templates&id=",
                                "fileTransferFolder": "/usr/local/tomcat/webapps/content/fileTransferFolder",
                                "lookInContext": 1,
                                "adminGroupID": 4,
                                "betaServer": True}}],
                    "servlet-mapping": {
                        "cofaxCDS": "/",
                        "cofaxEmail": "/cofaxutil/aemail/*",
                        "cofaxAdmin": "/admin/*",
                        "fileServlet": "/static/*",
                        "cofaxTools": "/tools/*"},

                    "taglib": {
                        "taglib-uri": "cofax.tld",
                        "taglib-location": "/WEB-INF/tlds/cofax.tld"}}},
                "data": {
                    "grade": grade
                }
            }
            schema = self.schema_generator.generate(json_dict=data,
                                                    request_params={"name": chr(65 + grade % 100)},
                                                    http_method=HTTPMethodKey.GET)
            self.record_map.add(schema)

        self.record_map.load()
        invariant_schema = self.record_map.generate_invariant_schema()
        pass
