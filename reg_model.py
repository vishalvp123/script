import sys
import xlrd
reg_name_list = [] #list to hold reg names
field_list = [] #list to hold field names
lsb_list = [] #list to hold lsb values of fields
msb_list = [] #list to hold msb values of fields
width_list = [] #list to hold width of fields
reset_val_list = [] #list to hold reset values of fields

#get the spreadsheet name from the user, which has the reg definitions
if len(sys.argv) == 2:
	filename = sys.argv[1]
else:
	filename = 'reg.xls'

workbook = xlrd.open_workbook("%s" %(filename))
worksheet = workbook.sheet_by_name('Sheet1')
rows = worksheet.nrows
columns = worksheet.ncols
print("rows = %d, columns = %d" %(rows,columns))
FW = open("reg_model.sv", "w")

for row_t in range(rows):
	for col_t in range(columns):
		elem = worksheet.cell(row_t,col_t)
		val = elem.value
		if val == "":
			break
		#print(val)
		#Collect all values from the spreadsheet into the lists declared above
		if val == "TOP MODULE":
			top_module_name = worksheet.cell(row_t,col_t+1).value
			print("Top Module name = %s" %top_module_name)
		
		if val == "REGISTER NAME":
			reg_name_list.append(worksheet.cell(row_t,col_t+1).value)
			reg_name = worksheet.cell(row_t, col_t+1).value
			#print("Reg name = %s" %reg_name)
			FW.write("class %s;\n\n" %(reg_name))
			FW.write("\treg [31:0] value;\n")
		
		if val == "FIELD NAME":	
			#lsb_list.append(worksheet.cell(row_t,col_t+2).value)
			lsb = worksheet.cell(row_t, col_t+2).value
			lsb_list.append(lsb)
			#print(lsb_list)
			width = worksheet.cell(row_t,col_t+3).value
			msb = width + lsb - 1
			msb_list.append(msb)

			reset_val_list.append(worksheet.cell(row_t,col_t+4).value)
			reset_val_name = worksheet.cell(row_t, col_t+4).value
			
			field_list.append(worksheet.cell(row_t,col_t+1).value)
			field_name = worksheet.cell(row_t, col_t+1).value
			#print("Reg name = %s" %reg_name)
			FW.write("\tbit [%d:%d] %s;\n" %(msb-lsb,0,field_name))
			#FW.write("\treg [31:0] value;\n")

		if val == "REG END":
			FW.write("\n\tfunction void reset();\n")
			num_fields = len(field_list)
			for i in range(num_fields):
				FW.write("\t\t%s = %s;\n" %(field_list[i],reset_val_list[i]))
			FW.write("\tendfunction\n\n")

			FW.write("\tfunction void write(reg [31:0] data);\n")
			FW.write("\t\tvalue = data;\n")
			for i in range(num_fields):
				msb_v = msb_list[i]
				lsb_v = lsb_list[i]
				#print(msb_list)
				FW.write("\t\t%s = data[%d:%d];\n" %(field_list[i],msb_list[i],lsb_list[i]))
			FW.write("\tendfunction\n\n")

			FW.write("\tfunction reg [31:0] read();\n")
			FW.write("\t\treturn value;\n")
			FW.write("\tendfunction\n\n")
			FW.write("endclass\n\n")
			field_list = []
			lsb_list = []
			reset_val_list = []
			msb_list = []
#print(lsb_list)
FW.write("class %s_Reg_Model;\n\n" %(top_module_name))
for reg in reg_name_list:
	FW.write("\t%s %s_i;\n" %(reg,reg))

#Reset reg
FW.write("\n\tfunction void reset_reg(reg [31:0] addr);\n")	
FW.write("\t\tcase(addr)\n")
for reg in reg_name_list:
	FW.write("\t\t\t`%s_ADDR : %s_i.reset();\n" %(reg,reg))
FW.write("\t\tendcase\n")	
FW.write("\tendfunction\n\n")
	

#Write reg
FW.write("\n\tfunction void write_reg(reg [31:0] addr, reg [31:0] data);\n")	
FW.write("\t\tcase(addr)\n")
for reg in reg_name_list:
	FW.write("\t\t\t`%s_ADDR : %s_i.write(data);\n" %(reg,reg))
FW.write("\t\tendcase\n")	
FW.write("\tendfunction\n\n")


#Read reg
FW.write("\n\tfunction reg [31:0] read_reg(reg [31:0] addr);\n")	
FW.write("\t\tcase(addr)\n")
for reg in reg_name_list:
	FW.write("\t\t\t`%s_ADDR : return %s_i.read();\n" %(reg,reg))
FW.write("\t\tendcase\n")	
FW.write("\tendfunction\n\n")


FW.write("endclass\n")	
