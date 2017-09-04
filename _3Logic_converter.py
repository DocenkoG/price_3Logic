# -*- coding: UTF-8 -*-
import os
import os.path
import logging
import logging.config
import io
import sys
import configparser
import time
#import openpyxl                       # Для .xlsx
import xlrd                            # для .xls


def make_loger():
    global log
    logging.config.fileConfig('logging.cfg')
    log = logging.getLogger('logFile')



def getCellXls(row, colName, sheet):
    global in_columns_j
    column=in_columns_j[colName]-1
    cell = sheet.cell(row, column)
    cellType  = cell.ctype
    cellValue = cell.value
    #
    #                                   дополнительная обработка поля.
    if cellType in (2,3) :
        if int(cellValue) == cellValue:
            ss = str(int(cellValue))
        else :
            ss = str(cellValue)
    elif colName in ('закупка','продажа','цена1', 'цена2') :
        ss = '0' 
    elif colName in ('наличие') and (cellValue == ''):
        ss = '0' 
    else : 
        ss = cellValue

    #elif cellType == 1 :
    #    ss = quoted(cellValue) 
    return ss


def convert2csv( myname ):
    global log
    global SheetName
    global FilenameIn
    global FilenameOut
    global out_columns_names
    global out_columns_j
    global in_columns_j
    global colGrp
    global colSGrp
    global GrpFonti
    global BrandFonti
    global SubGrpFonti
    global HeaderFonti
    global HeaderFontSize
    global RegularFontSize
    global SubGrpBackgroundColor
    global GrpBackgroundColor
    global strHeader
    global SubGrpFontSize
    global GrpFontSize
    make_loger()
    log.debug('Begin ' + __name__ + ' convert2csv')

    # Прочитать конфигурацию из файла
    ff = config_read( myname )
    log.debug('Открываю файл '+ FilenameIn)
#   book = openpyxl.load_workbook(filename = FilenameIn, read_only=False, keep_vba=False, data_only=False)
    book = xlrd.open_workbook( FilenameIn.encode('cp1251'), formatting_info=True)
    
    ssss = []

    log.debug('Устанавливаю страницу ' + SheetName )
    sh = book.sheet_by_name( SheetName )
    ssss = []
    line_qty = 0
    log.debug('   На ней строк  '+ str(sh.nrows))
                                                             # цикл по строкам страницы файла
    for i in range(0, sh.nrows) :
        line_qty += 1
        xfx = sh.cell_xf_index(i, 0)
        xf  = book.xf_list[xfx]
        bgcx  = xf.background.pattern_colour_index
        fonti = xf.font_index
        '''
        font = book.font_list[fonti]
        print( '---------------------- Строка', i, '-----------------------' )
        print( 'background_colour_index=',bgcx)
        print( 'fonti=', fonti)
        print( 'bold=', font.bold)
        print( 'weight=', font.weight)
        print( 'height=', font.height)
        print( 'italic=', font.italic)
        print( 'colour_index=', font.colour_index )
        print( 'name=', font.name)
        print( 'Строка', i, sh.cell(i, in_columns_j['раздел']-1).value)
        continue
        '''
        #print( sh.cell(i, in_columns_j[ out_columns_names['код']]).value)
        #print( out_columns_names['закупка'])
        #print( in_columns_j[ out_columns_names['закупка']] )
        #print( sh.cell(i, in_columns_j[ out_columns_names['закупка']]).ctype)
        #print( sh.cell(i, in_columns_j[ out_columns_names['закупка']]).value)


        if (fonti == HeaderFonti) :                                # Заголовок таблицы
            continue
        #if (fonti == BrandFonti) :                                # брэнд
        #    brandName = quoted(sh.cell(i,colGrp-1).value) 
        #    continue   
        #if (fonti == GrpFonti):                                    # Группа 
        #    grpName = quoted(sh.cell(i,colGrp-1).value)   
        #    subGrpName = ''
        #elif (fonti == SubGrpFonti):                               # подгруппа
        #    subGrpName = quoted(sh.cell(i,colGrp-1).value)        
        elif (     sh.cell(i, in_columns_j[ out_columns_names['закупка']]-1).ctype not in (2,3) ) or \
            ('' == sh.cell(i, in_columns_j[ out_columns_names['код']]-1).value ) :     # Пустая строка (нет кода или цены)
            #print('пустая')
            continue
        else :                                                     # Информационная строка
            sss = []                                               # формируемая строка для вывода в файл
            for strname in out_columns_names :
                #   сначала проверим вычисляемое ли это поле 
                if strname == 'подгруппа' :
                    s1 = getCellXls(i, 'подраздел1', sh)
                    s2 = getCellXls(i, 'подраздел2', sh)
                    ss = quoted(s1+' '+s2)
                    #print('подгруппа   : ',ss.encode(encoding='cp1251', errors='replace'))
                elif strname == 'наименование' :
                    s1 = getCellXls(i, 'раздел', sh)
                    s2 = getCellXls(i, 'бренд', sh)
                    s3 = getCellXls(i, 'partnumber', sh)
                    s4 = getCellXls(i, 'наименование', sh)
                    ss = quoted(s1+' '+s2+' '+s3+' '+s4)
                    #print('наименование: ',ss.encode(encoding='cp1251', errors='replace'))
                elif strname == 'описание' :
                    s1 = getCellXls(i, 'раздел', sh)
                    s2 = getCellXls(i, 'бренд', sh)
                    s3 = getCellXls(i, 'partnumber', sh)
                    s4 = getCellXls(i, 'наименование', sh)
                    ss = quoted(s1+' '+s2+' '+s3+' '+s4)
                #  теперь обычные транслируемые поля
                elif strname in out_columns_names :
                    #print( strname, out_columns_names[strname])
                    ss = getCellXls(i, out_columns_names[strname], sh)
                    ss = quoted(ss) 
                else:
                    ss = 'название вычисляемого поля = <' + strname +'>'
                
                sss.append(ss)
    
            #sss.append(brend)
            #sss.append(grpName)
            #sss.append(subGrpName)
            ssss.append(','.join(sss))
            #else :
            #    log.debug('Нераспознана строка: <' + sh.cell(row=i, column=out_columns_j['код']).value + '>' )
        #except Exception as e:
        #    log.debug('Exception: <' + str(e) + '> при обработке строки ' + str(i) +'<' + '>' )
        #    raise e

    
    f2 = open( FilenameOut, 'w', encoding='cp1251')
    f2.write(strHeader  + ',\n')
    data = ',\n'.join(ssss) +','
    dddd = data.encode(encoding='cp1251', errors='replace')
    data = dddd.decode(encoding='cp1251')
    f2.write(data)
    f2.close()



def config_read( myname ):
    global log
    global SheetName
    global FilenameIn
    global FilenameOut
    global out_columns_names
    global out_columns_j
    global in_columns_j
    global colGrp
    global colSGrp
    global GrpFonti
    global SubGrpFonti
    global BrandFonti
    global HeaderFonti
    global HeaderFontSize
    global RegularFontSize
    global SubGrpBackgroundColor
    global GrpBackgroundColor
    global strHeader
    global SubGrpFontSize
    global GrpFontSize

    cfgFName = myname + '.cfg'
    log.debug('Begin config_read ' + cfgFName )
    
    config = configparser.ConfigParser()
    if os.path.exists(cfgFName):     config.read( cfgFName)
    else : log.debug('Не найден файл конфигурации.')

    # в разделе [cols_in] находится список интересующих нас колонок и номера столбцов исходного файла
    in_columns_names = config.options('cols_in')
    in_columns_j = {}
    for vName in in_columns_names :
        if ('' != config.get('cols_in', vName)) :
            in_columns_j[vName] = config.getint('cols_in', vName) 
    
    # По разделу [cols_out] формируем перечень выводимых колонок и строку заголовка результирующего CSV файла
    temp_list = config.options('cols_out')
    out_columns_names = {}
    for vName in temp_list :
        if ('' != config.get('cols_out', vName)) :
            out_columns_names[vName] = config.get('cols_out', vName)
    
    #out_columns_j = {}
    #for vName in out_columns_names :
    #    tName = config.get('cols_out', vName)
    #    if  tName in in_columns_j :
    #        out_columns_j[vName] = in_columns_j[tName]
    #    else:
    #        out_columns_j[vName] = tName
    print('-----------------------------------')
    for vName in out_columns_names :
        print(vName, '\t', out_columns_names[vName])    
    print('-----------------------------------')
    strHeader = ','.join(out_columns_names)        # +',бренд,группа,подгруппа,'
    print('HEAD =', strHeader)

    # считываем имена файлов и имя листа
    FilenameIn   = config.get('input','Filename_in' )
    SheetName    = config.get('input','SheetName'   )      
    FilenameOut  = config.get('input','Filename_out')
    print('SHEET=', SheetName)
    
    # считываем признаки группы и подгруппы
    if ('' != config.get('grp_properties',  'группа')) :
        colGrp               = config.getint('grp_properties',     'группа')
    if ('' != config.get('grp_properties',  'подгруппа')) :
        colSGrp              = config.getint('grp_properties',  'подгруппа')
    if ('' != config.get('grp_properties',  'GrpFonti')) :
        GrpFonti             = config.getint('grp_properties',   'GrpFonti')
    if ('' != config.get('grp_properties',  'SubGrpFonti')) :
        SubGrpFonti          = config.getint('grp_properties','SubGrpFonti')
    if ('' != config.get('grp_properties',  'BrandFonti')) :
        BrandFonti           = config.getint('grp_properties', 'BrandFonti')
    if ('' != config.get('grp_properties',  'HeaderFonti')) :
        HeaderFonti          = config.getint('grp_properties','HeaderFonti')
    if ('' != config.get('grp_properties',  'HeaderFontSize')) :
        HeaderFontSize       = config.getint('grp_properties','HeaderFontSize')
    if ('' != config.get('grp_properties',  'RegularFontSize')) :
        RegularFontSize      = config.getint('grp_properties','RegularFontSize')
    if ('' != config.get('grp_properties',  'SubGrpFontSize')): 
        SubGrpFontSize       = config.getint('grp_properties','SubGrpFontSize')
    if ('' != config.get('grp_properties',  'GrpFontSize')) :
        GrpFontSize          = config.getint('grp_properties',   'GrpFontSize')
    if ('' != config.get('grp_properties',  'SubGrpBackgroundColor')) :
        SubGrpBackgroundColor= config.getint('grp_properties','SubGrpBackgroundColor')
    if ('' != config.get('grp_properties',  'GrpBackgroundColor')) :
        GrpBackgroundColor   = config.getint('grp_properties',   'GrpBackgroundColor')
    subgrpfontbold           = config.get('grp_properties','subgrpfontbold')
    grpfontbold              = config.get('grp_properties',   'grpfontbold')
    return FilenameIn



def quoted(sss):
    if ((',' in sss) or ('"' in sss) or ('\n' in sss))  and not(sss[0]=='"' and sss[-1]=='"') :
        sss = '"'+sss.replace('"','""')+'"'
    return sss