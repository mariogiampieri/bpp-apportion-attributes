import arcpy

arcpy.env.workspace = "C:\Users\mario\Documents/bpp\maps"
arcpy.env.overwriteOutput = True

census_blocks = "nyc_census_blocks_copy.shp"
precincts = "NYC_precincts_utm18_copy.shp"
census_lyr = "census_lyr"
precincts_lyr = "precincts_lyr"
c_diss_lyr = "cen_diss_lyr_w.shp"

arcpy.MakeFeatureLayer_management(precincts, precincts_lyr)
arcpy.MakeFeatureLayer_management(census_blocks, census_lyr)
pcursor = arcpy.da.SearchCursor(precincts_lyr, ["OID@", "precinct"])
ccursor = arcpy.da.SearchCursor(census_lyr, ["precinct", "POP10", "DP0110011"])
num_p = arcpy.GetCount_management(precincts_lyr)

for row in pcursor:
    each = row[0]
    print "precinct FID: ",each
    each_f = "FID=%s" %each
    sel_precinct = arcpy.SelectLayerByAttribute_management(precincts_lyr, "NEW_SELECTION", each_f)
    print "selected precinct"
    # select by location where centroid is within precinct polygon
    sel_cb = arcpy.SelectLayerByLocation_management(census_lyr, "HAVE_THEIR_CENTER_IN", sel_precinct, "", "NEW_SELECTION")
    count = int(arcpy.GetCount_management(sel_cb).getOutput(0))
    print "number of selected census blocks: ", count
    exp = row[-1]
    print "precinct number: ",exp
    # assign precinct number to selected polygons, then deselect
    print "writing precinct number to census blocks..."
    arcpy.CalculateField_management(sel_cb, "precinct", exp)

    #TODO:
    print "-----------------------------"

# for each in ccursor:
#     print each[1]
# sum and then add population to precinct polygon - dissolve based on precinct ID and then table join to precinct shape
arcpy.SelectLayerByAttribute_management(sel_cb, "CLEAR_SELECTION")
print "dissolving..."
arcpy.Dissolve_management(sel_cb, c_diss_lyr, dissolve_field="precinct", statistics_fields=[["POP10", 'SUM'], ["DP0110011", 'SUM']])

# join dissolved pop counts to precinct poly based on precinct field attribute