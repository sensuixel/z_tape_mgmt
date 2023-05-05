import re
import os
import dlm_reconciliation_parm as parm

from tabulate import tabulate

# Bitwise Functions
def print_binary(value, input_length):
    print(BitArray(int=value, length=input_length).bin)
    return

def test_mask(value, mask):
    return ((value ^ mask) ==0)

def set_bit(value, n):
    return value | (1 << n)

def get_bit(value, n):
    return ((value >> n & 1) != 0)


# Tape search Functions
def getOamDict(infile):
    rVolEntry = re.compile(r'^.*VOLUME-ENTRY----V(\w*)')
    rVolStatus = re.compile(r'^.*USE-ATTRIBUTE----(\w*)')
    tapeDict = {}
    with open(infile) as f:
        for line in f:
            if rVolEntry.match(line):
                volEnt = rVolEntry.match(line).group(1)
                # Search Next line for USE-ATTRIBUTE
                while not rVolStatus.match(line):
                    line = next(f)
                volStatus = rVolStatus.match(line).group(1)
                tapeDict[volEnt] = volStatus
    return tapeDict

# JCL Functions
def generateRMMDV(tape_list, lpar, media_type):
    jclFile = os.path.join(parm.JCL_PATH, "{}_DLMSCR_{}.jcl".format(media_type, lpar))
    with open(jclFile, 'w') as rmmdv_file:
        # Add job_card
        rmmdv_file.write(parm.job_card.format(lpar) + "\n")

        # Add xeq_card
        rmmdv_file.write(parm.xeq_card.format(parm.XEQ_Dict[lpar]) + "\n")

        # Add RMMDV Step
        rmmdv_file.write(parm.rmmdv_step.format(parm.DRIVER_DLM[media_type]) + "\n")

        # Generate SYSIN
        rmmdv_sysin = [ parm.rmmdv_command.format(tape) for tape in tape_list ]
        rmmdv_file.write('\n'.join(rmmdv_sysin) + "\n")
        
    return

def generateRMMDVAndAlterVOLENT(tape_list, lpar, media_type):
    jclFile = os.path.join(parm.JCL_PATH, "{}_DLMSCR_ALTERVOLENT_{}.jcl".format(media_type, lpar))
    with open(jclFile, 'w') as rmmdv_file:
        # Add job_card
        rmmdv_file.write(parm.job_card.format(lpar) + "\n")

        # Add xeq_card
        rmmdv_file.write(parm.xeq_card.format(parm.XEQ_Dict[lpar]) + "\n")

        # Add RMMDV Step
        rmmdv_file.write(parm.rmmdv_step.format(parm.DRIVER_DLM[media_type]) + "\n")

        # Generate SYSIN
        rmmdv_sysin = [ parm.rmmdv_command.format(tape) for tape in tape_list ]
        rmmdv_file.write('\n'.join(rmmdv_sysin) + "\n")

        # Add alter volent step
        rmmdv_file.write(parm.alter_volent_step + "\n")

        # Generate SYSIN
        alter_volent_sysin = [ parm.alter_volent_command.format(tape) for tape in tape_list ]
        rmmdv_file.write('\n'.join(alter_volent_sysin) + "\n")


# Test
def generateHtmlTable(html_title, html_file, html_data):
    with open(html_file, 'w', encoding='cp1047') as html_page:
        # Add title
        html_page.write(parm.html_start.format(html_title))
        # Generate Table
        html_page.write(tabulate(html_data ,headers='firstrow' ,tablefmt='html') + "\n")
        # End page
        html_page.write(parm.html_end)
        return
