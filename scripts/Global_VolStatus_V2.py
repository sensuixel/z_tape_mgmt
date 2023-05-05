# -*- coding: utf-8 -*-
import argparse
import os
import glob
import re

from datetime import datetime
from os import path

from dlm_reconciliation_functions import *
import dlm_reconciliation_parm as parm

# Parse input argument
parser = argparse.ArgumentParser(prog = 'Global_VolStatus_V2.py',
                                 description='Compare tape status in CTT/OAM and DLM or CRS and Generate JCL to correct errors')
parser.add_argument('-mediatype', '--mediatype', help='Select DLM or CRS') 
args = parser.parse_args()

# Check Media Type
if args.mediatype not in parm.VALID_MEDIA_TYPE:
    print("Media Type {} Incorrect".format(args.mediatype))
    print("Values accepted are : {}".format(' or '.join(parm.VALID_MEDIA_TYPE)))
    exit()

# Constants :
MEDIA_TYPE = args.mediatype
default_status = 0b000000 # not found everywhere / scratch everywhere

# Compile regex
rex_dlm_tape = re.compile(r"^\s+\d*\s*([A-Z]|" + re.escape(parm.SCRATCH_CHAR) + "[A-Z])\d{5}\s*")
rex_ctt = re.compile(r"^\s*([A-Z]{1}\d{5})\s*(" + re.escape(MEDIA_TYPE) + ")\s*(\w*)")
rex_oam_tape = re.compile(r"'^.*VOLUME-ENTRY----V(\w*)")
rex_oam_scratch = re.compile(r"^.*USE-ATTRIBUTE----(\w*)")

#=================================================================#
#
# 1. Verify if each lpar has a CTT File and a DLM CP503 file
#   - Check if all lpar have :
#       - CTTRPT File
#       - OAM List volume file
#       - DLM CP503 file
#   => Only the lpar who have 3 files will be processed
#
#=================================================================#
# 1.1 List all known LPAR declared in XEQ_Dict in dlm_reconciliation_parm.py
full_lpar_dict = { lpar:0 for lpar in list ( parm.XEQ_Dict.keys()) }

# 1.2 For all lpar check if the 3 files exist.
for lpar in full_lpar_dict.keys():
    # Test if cp503 file exist :
    if path.exists(os.path.join(parm.CP503_PATH, "cp503_{}_{}.txt".format(MEDIA_TYPE, lpar))):
        full_lpar_dict[lpar] += 1
    # Test if CTT file exist :
    if path.exists(os.path.join(parm.CTT_PATH, "ctt_{}.txt".format(lpar))):
        full_lpar_dict[lpar] += 1
    # Test if OAM file exist :
    if path.exists(os.path.join(parm.OAM_PATH, "oam_{}_{}.txt".format(MEDIA_TYPE, lpar))):
        full_lpar_dict[lpar] += 1

# 1.3 Build the list of lpar that will be processed
full_lpar_list = [ lpar for lpar,file_count in full_lpar_dict.items() if file_count == 3 ]
error_lpar_list = [ lpar for lpar,file_count in full_lpar_dict.items() if file_count != 3 ]

print("Following Lpar will be processed")
print("\n".join(full_lpar_list))
print("Following lpar cannot be processed due to missing file")
print("\n".join(error_lpar_list))


#=================================================================#
#
# 2. For all Lpar :
#   => Read CTT File then OAM file then DLM file to build a dict
#       - Key = Tape Name
#       - Value = bitmask of 6 bits
#            bit 0 = 0 Scracth in ctt / 1 Private in ctt
#            bit 1 = 0 Scracth in oam / 1 Private in oam
#            bit 2 = 0 Scracth in dlm / 1 Private in dlm
#            bit 3 = 0 Not found in ctt / 1 Found in ctt
#            bit 4 = 0 Not found in oam / 1 Found in oam
#            bit 5 = 0 Not found in dlm / 1 Found in dlm
#
#=================================================================#
# 2.1 Define list to hold stats for all lpar
lpar_stats_nested_list = [ ["Lpar", "Tape_Location", "Defined_Tape", "Scratch_Tape", "Private_Tape", "Scratch+Private"],
                           ]

# 2.2 Loop on all lpar
for lpar in full_lpar_list:
    # Declare all file name
    cttFile = os.path.join(parm.CTT_PATH, 'ctt_{}.txt'.format(lpar))
    oamFile = os.path.join(parm.OAM_PATH, 'oam_{}_{}.txt'.format(MEDIA_TYPE, lpar))
    cp503File = os.path.join(parm.CP503_PATH,'cp503_{}_{}.txt'.format(MEDIA_TYPE, lpar))
    
    # Init Dict of lpar
    full_tape_dict = {}
    
    # 1. Read CTT File    
    with open(cttFile) as ctt_file:
        for line in ctt_file:
            # Filter only tape line
            line_match = rex_ctt.match(line)

            # Parse tape / media type (DLM|CRS) / State = Scratch/Active/Edm control
            if line_match:
                # Mark as Found in CTT
                status = set_bit(default_status, 3)
                # Parse data
                tape = line_match.group(1)
                media = line_match.group(2)
                tape_status = line_match.group(3)
                
                # Check if tape is Private/Scratch
                if tape_status != "Scratch":
                    # Mark as private in CTT
                    status = set_bit(status, 0)
                # Add tape
                full_tape_dict[tape] = status
    
    # 2. Read OAM File and update the main dict accordingly
    oam_data = getOamDict(oamFile)
    # Updatefull_tape_dict
    for oam_tape, oam_status in oam_data.items():
        # Is tape already in dict ?
        if oam_tape in full_tape_dict.keys():
            full_tape_dict[oam_tape] = set_bit(full_tape_dict[oam_tape], 4)
        else:
            full_tape_dict[oam_tape] = set_bit(default_status, 4)
            
        # Check tape status in oam and update accordingly
        if oam_status == "PRIVATE":
            full_tape_dict[oam_tape] = set_bit(full_tape_dict[oam_tape], 1)
    
    # 3. Read cp503 File and update the main dict accordingly
    with open(cp503File) as cp503_file:
        # Read line and filter only on tape
        for line in cp503_file:
            # Tape found in dlm            
            if rex_dlm_tape.match(line):
                # Parse tape name
                dlm_tape = line.split()[1]
                dlm_scratch = False

                # Test if tape is scrath/private
                if dlm_tape.startswith(parm.SCRATCH_CHAR):
                    dlm_tape = dlm_tape[1:]
                    dlm_scratch = True

                # Update dict
                if dlm_tape in full_tape_dict.keys():
                    full_tape_dict[dlm_tape] = set_bit(full_tape_dict[dlm_tape], 5)
                else:
                    full_tape_dict[dlm_tape] = set_bit(default_status, 5)
                
                # Mark as private or scratch in DLM
                if not dlm_scratch:
                    full_tape_dict[dlm_tape] = set_bit(full_tape_dict[dlm_tape], 2)

    ##=================================================================#
    #
    # 3. Control Each lpar :
    #   -  List tape scratch in CTT and OAM but not in DLM 
    #   -  List tape scratch in CTT but not in OAM and DLM
    #   -  List Tape Initialized in DLM but not in CTT and OAM 
    #
    #=================================================================#
    # full_tape_dict is now populated
    # Define Bit Mask
    mask_not_scratch_in_dlm = 0b111100
    mask_not_scratch_in_oam_and_dlm = 0b111110
    mask_tape_only_in_dlm_private = 0b100100
    mask_tape_only_in_dlm_scracth = 0b100000

    # List tape for each type
    ctt_tape_defined_list = [ tape for tape, status in full_tape_dict.items() if get_bit(status, 3) ]
    ctt_tape_scratch_list = [ tape for tape, status in full_tape_dict.items() if not get_bit(status, 0) ]
    ctt_tape_private_list = [ tape for tape, status in full_tape_dict.items() if get_bit(status, 0) ]

    oam_tape_defined_list = [ tape for tape, status in full_tape_dict.items() if get_bit(status, 4) ]
    oam_tape_scratch_list = [ tape for tape, status in full_tape_dict.items() if not get_bit(status, 1) ]
    oam_tape_private_list = [ tape for tape, status in full_tape_dict.items() if get_bit(status, 1) ]

    dlm_tape_defined_list = [ tape for tape, status in full_tape_dict.items() if get_bit(status, 5) ]
    dlm_tape_scratch_list = [ tape for tape, status in full_tape_dict.items() if not get_bit(status, 2) ]
    dlm_tape_private_list = [ tape for tape, status in full_tape_dict.items() if get_bit(status, 2) ]

    # Add element to stats list
    # ["Lpar", "Tape_Location", "Defined_Tape", "Scratch_Tape", "Private_Tape", "Scratch+Private"]
    lpar_stats_nested_list.append( [ lpar, "CTT",
                                     len(ctt_tape_defined_list),
                                     len(ctt_tape_scratch_list),
                                     len(ctt_tape_private_list),
                                     len(ctt_tape_scratch_list) + len(ctt_tape_private_list)
                                     ]
                                   )
    lpar_stats_nested_list.append( [ lpar, "OAM",
                                     len(oam_tape_defined_list),
                                     len(oam_tape_scratch_list),
                                     len(oam_tape_private_list),
                                     len(oam_tape_scratch_list) + len(oam_tape_private_list)
                                     ]
                                   )
    lpar_stats_nested_list.append( [ lpar, MEDIA_TYPE,
                                     len(dlm_tape_defined_list),
                                     len(dlm_tape_scratch_list),
                                     len(dlm_tape_private_list),
                                     len(dlm_tape_scratch_list) + len(dlm_tape_private_list)
                                     ]
                                   )

    # List tape in bad status 
    tape_not_scratch_in_dlm = [ tape for tape, status in full_tape_dict.items() if test_mask(status, mask_not_scratch_in_dlm) ]
    tape_not_scratch_in_oam_and_dlm = [ tape for tape, status in full_tape_dict.items() if test_mask(status, mask_not_scratch_in_oam_and_dlm) ]
    tape_only_in_dlm = [ tape for tape, status in full_tape_dict.items() if test_mask(status, mask_tape_only_in_dlm_private) or  test_mask(status, mask_tape_only_in_dlm_scracth)]
    
    # Generate JCL
    if tape_not_scratch_in_dlm:
        generateRMMDV(tape_not_scratch_in_dlm, lpar, MEDIA_TYPE)
        print("RMMDV JCL for lpar {} generated in {}".format(lpar, parm.JCL_PATH))
    if tape_not_scratch_in_oam_and_dlm:
        generateRMMDVAndAlterVOLENT(tape_not_scratch_in_oam_and_dlm, lpar, MEDIA_TYPE)
        print("RMMDV and Alter VOLENT JCL for lpar {} generated in {}".format(lpar, parm.JCL_PATH))

##=================================================================#
#
# 4. Print report
#
##=================================================================#
generateHtmlTable('Scratch Report', os.path.join(parm.REPORT_PATH, 'dlmscratch_report_{}.html'.format(MEDIA_TYPE)) , lpar_stats_nested_list)
exit()
