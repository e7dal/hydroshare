# -*- coding: utf-8 -*-
"""
Test name canonicalization
"""

from unittest import TestCase
from hs_core.search_indexes import normalize_name


class NameTest(TestCase):

    def setUp(self):
        pass

    def test_basic_canonicalization(self):
        # This is a list of names and their canonicalizations.
        names = [
            ["Aaron Shiels", "Shiels, Aaron"],
            ["A. Hendrick", "Hendrick, A."],
            ["Alain F. Plante", "Plante, Alain F."],
            ["Alain F.Plante", "Plante, Alain F."],
            ["Alexander K. Loomis", "Loomis, Alexander K."],
            ["Alonso Ramírez", "Ramírez, Alonso"],
            ["Álvarez-Berríos, Nora L.", "Álvarez-Berríos, Nora L."],
            ["Anderson, B. A.", "Anderson, B. A."],
            ["Andrew C. Kurtz", "Kurtz, Andrew C."],
            ["Angel Torres-Sanchez", "Torres-Sanchez, Angel"],
            ["Calhoun Critical Zone Observatory", "Calhoun Critical Zone Observatory"],
            ["Colorado's Surface Water Conditions", "Colorado's Surface Water Conditions"],
            [" Damiano, S.G.", "Damiano, S. G."],
            ["Damiano, S. G.", "Damiano, S. G."],
            ["Damiano, S.G.", "Damiano, S. G."],
            ["Daniel deB Richter", "Richter, Daniel deB"],
            ["Department of Commerce (DOC)", "Department of Commerce (DOC)"],
            ["Duffy, Chistopher", "Duffy, Chistopher"],
            ["Duffy, Chris", "Duffy, Chris"],
            ["Duffy, Christopher J.", "Duffy, Christopher J."],
            ["Duncan, Jon", "Duncan, Jon"],
            ["Eel River CZO", "Eel River CZO"],
            ["G.E. Likens", "Likens, G. E."],
            ["Greg Barron-Gafford", "Barron-Gafford, Greg"],
            ["Grizelle Gonzalez", "Gonzalez, Grizelle"],
            ["Grizelle González", "González, Grizelle"],
            ["Hasenmueller, Elizabeth A.", "Hasenmueller, Elizabeth A."],
            [" Idaho State University", "Idaho State University"],
            [" IITF ", "IITF"],
            ["Ingo Heidbuechel", "Ingo Heidbuechel"],  # miscategorized as corporation
            ["Luquillo Critical Zone Observatory", "Luquillo Critical Zone Observatory"],
            ["M. Yekta", "M. Yekta"],
            ["NADP", "NADP"],
            ["National Ocean Service (NOS)", "National Ocean Service (NOS)"],
            ["National Park Service", "National Park Service"],
            ["Niwot Ridge LTER", "Niwot Ridge LTER"],
            ["NOAA", "NOAA"],
            ["NOAA's National Climatic Data Center", "NOAA's National Climatic Data Center"],
            ["Oshun, Jasper", "Oshun, Jasper"],
            ["others", "others"],
            ["Philip A.E. Pogge von Strandmann", "Philip A.E. Pogge von Strandmann"],
            [" Phillips, C.B. ", "Phillips, C. B."],
            ["Quiñones, Maya,", "Quiñones, Maya"],
            ["Rebecca Flournoy", "Flournoy, Rebecca"],
            ["Rebecca Minor", "Minor, Rebecca"],
            ["Rempe, Daniella", "Rempe, Daniella"],
            ["Rena Stair", "Stair, Rena"],
            ["Reynolds Creek CZO", "Reynolds Creek CZO"],
            ["Richardson, D.", "Richardson, D."],
            ["Rich Brereton", "Brereton, Rich"],
            ["Richter, Daniel", "Richter, Daniel"],
            ["Richter, Daniel deB.", "Richter, Daniel deB."],
            ["Richter, Daniel deB", "Richter, Daniel deB"],
            ["Richter, D. deB.", "Richter, D. deB."],
            ["Richter, D. deB", "Richter, D. deB"],
            ["Robert F. Stallard", "Stallard, Robert F."],
            ["Robert Parmenter", "Parmenter, Robert"],
            ["Roger Bales", "Bales, Roger"],
            ["Roman DiBiase", "DiBiase, Roman"],
            ["Rood, Dylan H.", "Rood, Dylan H."],
            ["Russo, Tess", "Russo, Tess"],
            [" Shale Hills Critical Zone Observatory", "Shale Hills Critical Zone Observatory"],
            ["Shale Hills Critical Zone Observatory", "Shale Hills Critical Zone Observatory"],
            ["Shale Hills CZO", "Shale Hills CZO"],
            ["Sharon Billings", "Billings, Sharon"],
            ["Sharon Cantrell", "Cantrell, Sharon"],
            ["S. Havens", "Havens, S."],
            ["Stone, M.M.", "Stone, M. M."],
            ["Stromberg, Mark", "Stromberg, Mark"],
            ["Stroud Water Research Center", "Stroud Water Research Center"],
            ["Stuemky, M.", "Stuemky, M."],
            ["Sue Brantley", "Brantley, Sue"],
            ["Susan Brantley", "Brantley, Susan"],
            ["Susan L Brantley", "Brantley, Susan L"],
            ["Susan L. Brantley", "Brantley, Susan L."],
            ["Susan Yetter", "Yetter, Susan"],
            ["Sutter, Lori", "Sutter, Lori"],
            ["Suzanne Anderson", "Anderson, Suzanne"],
            ["Sweeney, B.", "Sweeney, B."],
            ["Szabo, Timea", "Szabo, Timea"],
            ["Tang, Qicheng", "Tang, Qicheng"],
            ["Tess Russo", "Russo, Tess"],
            ["Thomas, Evan", "Thomas, Evan"],
            ["Thomas, Evan M.", "Thomas, Evan M."],
            ["Thompson, A.", "Thompson, A."],
            ["Timothy Corley", "Corley, Timothy"],
            ["Timothy D. Schowalter", "Schowalter, Timothy D."],
            ["Todd, Dawson E.", "Todd, Dawson E."],
            ["Toran, Laura", "Toran, Laura"],
            ["Torres-Sánchez, Angel", "Torres-Sánchez, Angel"],
            ["Torres-Sanchez, Angel J. ", "Torres-Sanchez, Angel J."],
            ["T. Parzybok", "T. Parzybok"],
            ["Treffkorn, Jonathan", "Treffkorn, Jonathan"],
            ["Tsang, Y-P", "Tsang, Y-P"],
            ["Tyson Lee Swetnam", "Swetnam, Tyson Lee"],
            ["University of Arizona", "University of Arizona"],
            ["University of California Merced", "University of California Merced"],
            ["U.S. Army Corps of Engineers (USACE)", "U.S. Army Corps of Engineers (USACE)"],
            ["USDA-ARS", "USDA-ARS"],
            ["USDA USFS", "USDA USFS"],
            ["U.S. Department of Agriculture", "U.S. Department of Agriculture"],
            ["US Geological Survey", "US Geological Survey"],
            ["USGS", "USGS"],
            ["USGS NWIS", "USGS NWIS"],
            ["Valles Caldera National Preserve", "Valles Caldera National Preserve"],
            ["Wadsworth, Frank H.", "Wadsworth, Frank H."],
            ["Weitzman, Julie", "Weitzman, Julie"],
            ["West, H.", "West, H."],
            ["Whendee L. Silver", "Silver, Whendee L."],
            ["Whendee Silver", "Silver, Whendee"],
            ["White, Tim", "White, Tim"],
            ["W.H. McDowell", "McDowell, W. H."],
            ["William Dietrich", "Dietrich, William"],
            ["William G. McDowell", "McDowell, William G."],
            ["William H McDowell", "McDowell, William H"],
            ["Williams, Jennifer", "Williams, Jennifer"],
            ["William Wright", "Wright, William"],
            ["Will, R.M.", "Will, R. M."],
            ["W. L. Silver", "Silver, W. L."],
            ["Wong, Christopher S.", "Wong, Christopher S."],
            ["Xavier Comas", "Comas, Xavier"],
            ["Xavier Zapata-Rios", "Zapata-Rios, Xavier"],
            ["Zreda, Marek", "Zreda, Marek"],
            ["Z.S. Brecheisen", "Brecheisen, Z. S."]
        ]
        for n in names:
            result = normalize_name(n[0])
            self.assertEqual(result, n[1])
