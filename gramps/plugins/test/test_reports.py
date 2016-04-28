#! /usr/bin/env python3
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (c) 2016 Gramps Development Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

import unittest
import os
import shutil

from gramps.test.test_util import Gramps

ddir = os.path.dirname(__file__)
example = os.path.join(ddir, "..", "..", "..",
                       "example", "gramps", "data.gramps")
sample = os.path.join(ddir, "..", "..", "..",
                      "example", "gedcom", "sample.ged")

TREE_NAME = "Test_reporttest"

class ReportControl(object):
    def tearDown(self):
        out, err = self.call("-y", "--remove", TREE_NAME)
        out, err = self.call("-y", "--remove", TREE_NAME + "_import_gedcom")

    def call(self, *args):
        print("call:", args)
        self.gramps = Gramps()
        out, err = self.gramps.run(*args)
        print("out:", out, "err:", err)
        return out, err

    def __init__(self):
        super().__init__()
        self.tearDown() # removes it if it existed
        out, err = self.call("-C", TREE_NAME,
                             "--import", example)
        out, err = self.call("-O", TREE_NAME,
                             "--action", "report",
                             "--options", "show=all")
        self.reports = []
        for line in err.split("\n"):
            if line.startswith("   "):
                report_name, description = line.split("- ", 1)
                self.reports.append(report_name.strip())

    def addreport(self, class_, report_name, test_function,
                  files, **options):
        test_name = report_name.replace("-", "_")
        setattr(class_, test_name, dynamic_report_method(
            report_name,
            test_function,
            files,
            "--force",
            "-O", TREE_NAME,
            "--action", "report",
            "--options", "name=%s" % report_name,
            **options))

    def addcli(self, class_, report_name, test_function,
               files, *args, **options):
        test_name = report_name.replace("-", "_")
        setattr(class_, test_name, 
                dynamic_cli_method(
                    report_name,
                    test_function,
                    files,
                    *args))

def dynamic_report_method(report_name, test_function,
                          files, *args, **options):
    args = list(args)
    args[-1] += "," + (",".join(["%s=%s" % (k, v) for (k,v) in options.items()]))
    options["files"] = files
    # This needs to have "test" in name:
    def test_method(self):
        out, err = self.call(*args)
        self.assertTrue(test_function(out, err, report_name, **options))
    return test_method

def dynamic_cli_method(report_name, test_function,
                       files, *args, **options):
    options["files"] = files
    # This needs to have "test" in name:
    def test_method(self):
        out, err = self.call(*args)
        self.assertTrue(test_function(out, err, report_name, **options))
    return test_method

class TestDynamic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            os.makedirs("temp")
        except:
            pass

    @classmethod
    def call(cls, *args):
        print("call:", args)
        gramps = Gramps()
        out, err = gramps.run(*args)
        print("out:", out, "err:", err)
        return out, err

    @classmethod
    def tearDownClass(cls):
        out, err = cls.call("-y", "--remove", TREE_NAME)
        out, err = cls.call("-y", "--remove", TREE_NAME + "_import_gedcom")

reports = ReportControl()

def report_contains(text):
    def test_output_file(out, err, report_name, **options):
        ext = options["off"]
        with open(report_name + "." + ext) as fp:
            contents = fp.read()
        print(contents)
        if options.get("files", []):
            for filename in options.get("files", []):
                if filename is None:
                    pass
                elif os.path.isdir(filename):
                    shutil.rmtree(filename)
                elif os.path.isfile(filename):
                    os.remove(filename)
                else:
                    raise Exception("can't find '%s' in order to delete it" % filename)
        elif os.path.isfile(report_name + "." + ext):
            os.remove(report_name + "." + ext)
        else:
            raise Exception("can't find '%s' in order to delete it" % (report_name + "." + ext))
        return text in contents
    return test_output_file

def err_does_not_contain(text):
    def test_output_file(out, err, report_name, **options):
        if options.get("files", []):
            for filename in options.get("files", []):
                if filename is None:
                    pass
                elif os.path.isdir(filename):
                    shutil.rmtree(filename)
                elif os.path.isfile(filename):
                    os.remove(filename)
                else:
                    raise Exception("can't find '%s' in order to delete it" % filename)
        else:
            ext = options["off"]
            if os.path.isfile(report_name + "." + ext):
                os.remove(report_name + "." + ext)
            else:
                raise Exception("can't find '%s' in order to delete it" % (report_name + "." + ext))
        return text not in err
    return test_output_file

def err_does_contain(text):
    def test_output_file(out, err, report_name, **options):
        if options.get("files", []):
            for filename in options.get("files", []):
                if filename is None:
                    pass
                elif os.path.isdir(filename):
                    shutil.rmtree(filename)
                elif os.path.isfile(filename):
                    os.remove(filename)
                else:
                    raise Exception("can't find '%s' in order to delete it" % filename)
        else:
            ext = options["off"]
            if os.path.isfile(report_name + "." + ext):
                os.remove(report_name + "." + ext)
            else:
                raise Exception("can't find '%s' in order to delete it" % (report_name + "." + ext))
        return text in err
    return test_output_file

reports.addreport(TestDynamic, "tag_report",
                  report_contains("I0037  Smith, Edwin Michael"),
                  [],
                  off="txt", tag="tag1")

reports.addreport(TestDynamic, "navwebpage",
                  err_does_not_contain("Failed to write report."),
                  ["/tmp/NAVWEB"],
                  off="html", target="/tmp/NAVWEB")

reports.addcli(TestDynamic, "import_gedcom",
               err_does_contain("Cleaning up."),
               [None],
               "-C", TREE_NAME + "_import_gedcom",
               "--import", sample)

reports.addcli(TestDynamic, "export_gedcom",
               err_does_contain("Cleaning up."),
               ["test_export.ged"],
               "--force",
               "-O", TREE_NAME,
               "--export", "test_export.ged")

# reports.addcli(TestDynamic, "export_csv",
#                err_does_contain("Cleaning up."),
#                ["test_export.csv"],
#                "--force",
#                "-O", TREE_NAME,
#                "--export", "test_export.csv")

# reports.addcli(TestDynamic, "export_wtf",
#                err_does_contain("Cleaning up."),
#                ["test_export.wtf"],
#                "--force",
#                "-O", TREE_NAME,
#                "--export", "test_export.wtf")

reports.addcli(TestDynamic, "export_gw",
               err_does_contain("Cleaning up."),
               ["test_export.gw"],
               "--force",
               "-O", TREE_NAME,
               "--export", "test_export.gw")

reports.addcli(TestDynamic, "export_gpkg",
               err_does_contain("Cleaning up."),
               ["test_export.gpkg"],
               "--force",
               "-O", TREE_NAME,
               "--export", "test_export.gpkg")

reports.addcli(TestDynamic, "export_vcs",
               err_does_contain("Cleaning up."),
               ["test_export.vcs"],
               "--force",
               "-O", TREE_NAME,
               "--export", "test_export.vcs")

reports.addcli(TestDynamic, "export_vcf",
               err_does_contain("Cleaning up."),
               ["test_export.vcf"],
               "--force",
               "-O", TREE_NAME,
               "--export", "test_export.vcf")

report_list = [
    ##("ancestor_chart", "pdf", []), # Ancestor Tree
    ("ancestor_report", "txt", []), # Ahnentafel Report
    ("birthday_report", "txt", []), # Birthday and Anniversary Report
    # ("calendar", "svg", ["calendar-10.svg", "calendar-11.svg",
    #                      "calendar-12.svg", "calendar-2.svg",
    #                      "calendar-3.svg", "calendar-4.svg",
    #                      "calendar-5.svg", "calendar-6.svg",
    #                      "calendar-7.svg", "calendar-8.svg",
    #                      "calendar-9.svg"]), # Calendar
    ## ("d3-ancestralcollapsibletree", "txt"), # Ancestral Collapsible Tree
    ## ("d3-ancestralfanchart", "txt"), # Ancestral Fan Chart
    ## "d3-descendantindentedtree", # Descendant Indented Tree
    ### ("database-differences-report", "txt", []), # Database Differences Report
    ## "denominoviso", # DenominoViso
    ##("descend_chart", "svg", []), # Descendant Tree
    ("descend_report", "txt", []), # Descendant Report
    ### ("DescendantBook", "txt", []), # Descendant Book
    ## ("Descendants Lines", "txt"), # Descendants Lines
    ("det_ancestor_report", "txt", []), # Detailed Ancestral Report
    ("det_descendant_report", "txt", []), # Detailed Descendant Report
    ### ("DetailedDescendantBook", "txt", []), # Detailed Descendant Book
    ## ("DynamicWeb", "txt"), # Dynamic Web Report
    ("endofline_report", "txt", []), # End of Line Report
    ##("family_descend_chart", "svg", []), # Family Descendant Tree
    ("family_group", "txt", []), # Family Group Report
    ##("familylines_graph", "svg", []), # Family Lines Graph
    # ("FamilyTree", "svg", []), # Family Tree
    # ("fan_chart", "svg", []), # Fan Chart
    # ("hourglass_graph", "svg", []), # Hourglass Graph
    ("indiv_complete", "txt", []), # Complete Individual Report
    ("kinship_report", "txt", []), # Kinship Report
    ### ("LastChangeReport", "txt", []), # Last Change Report
    ### ("LinesOfDescendency", "txt", []), # Lines of Descendency Report
    ## "ListeEclair", # Tiny Tafel
    ("notelinkreport", "txt", []), # Note Link Report
    ("number_of_ancestors", "txt", []), # Number of Ancestors Report
    ##("PedigreeChart", "svg", ["PedigreeChart-2.svg"]), # Pedigree Chart
    ### ("PersonEverythingReport", "txt", []), # PersonEverything Report
    ## "place_report", # Place Report
    ("records", "txt", []), # Records Report
    ##("rel_graph", "pdf", []), # Relationship Graph
    ### ("Repositories Report", "txt", []), # Repositories Report
    ### ("Repositories Report Options", "txt", []), # Repositories Report Options
    # ("statistics_chart", "svg", ["statistics_chart-2.svg",
    #                              "statistics_chart-3.svg"]), # Statistics Charts
    ("summary", "txt", []), # Database Summary Report
    ##("timeline", "pdf", []), # Timeline Chart
    ### ("TodoReport", "txt", []), # Todo Report
    ## ("WebCal", "txt"), # Web Calendar
]

for (report_name, off, files) in report_list:
    reports.addreport(TestDynamic, report_name,
                      err_does_not_contain("Failed to write report."),
                      files=files,
                      off=off)

if __name__ == "__main__":
    unittest.main()