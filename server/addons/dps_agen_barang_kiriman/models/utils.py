from odoo import models, fields, api,_
import math
from datetime import date,datetime,timedelta 
import json
import pytz

def round_thousand(x) :
    return int(math.ceil(x / 1000.0)) * 1000

def load_data(sheet):
    data = []
    offset = 0
    for row in range(sheet.nrows) :
        if row-offset ==0 :
            col_codes = []
            for col in range(sheet.ncols) :
                value = sheet.cell(row,col).value
                if type(value) == str :
                    value = value.strip()
                col_codes.append(value)
        elif row-offset > 0 :
            new_line = {}
            for col in range(sheet.ncols) :
                new_line[col_codes[col]] = sheet.cell(row,col).value
            data.append(new_line)
    return data

def get_id(self,code,master) :
    obj = self.env['dps.reference'].search([('name','=',code),('kode_master','=',master)])
    if obj :
        hasil = obj.id
    else :
        hasil = None
    return hasil

def get_tanggal(tanggal) :
    type_tanggal = type(tanggal)
    if tanggal :
        if type_tanggal == float :
            hitung_tgl = (tanggal - 25569) * 86400
            tgl = datetime.utcfromtimestamp(hitung_tgl).date()
        else :
            tgl = tanggal.strip()
            tanggal = datetime.strptime(tgl, '%d-%m-%Y').strftime('%m/%d/%Y')
    else : 
        tanggal = None
    return tanggal

def ctanggal_billing(tanggal) :
    if tanggal :
        tgl = datetime.strptime(str(tanggal), '%d-%m-%Y').strftime('%m/%d/%Y')
    else :
        tgl = ""
    return tgl

def ctanggal_billing_new(tanggal) :
    if tanggal :
        tgl = datetime.strptime(str(tanggal), '%Y-%m-%d %H:%M:%S.0').strftime('%m/%d/%Y')
    else :
        tgl = ""
    return tgl

def cdatetime_local(tanggal):
    if tanggal :
        tgl = datetime.strptime(str(tanggal), '%Y/%m/%d %H:%M:%S') + timedelta(hours=-7)
    else :
        tgl = ""
    return tgl

def cdatetime_billing(tanggal) :
    if tanggal :
        tgl = datetime.strptime(str(tanggal), '%d-%m-%Y %H:%M:%S').strftime('%m/%d/%Y %H:%M:%S') 
        # ctgl = tgl + timedelta(hours=-7)
        tgl = datetime.strptime(str(tgl), '%m/%d/%Y %H:%M:%S') + timedelta(hours=-7)
        # print(ctgl)
    else :
        tgl = ""
    return tgl

def ctanggal(tanggal) :
    if tanggal :
        tgl = datetime.strptime(str(tanggal), '%Y-%m-%d').strftime('%Y/%m/%d')
    else :
        tgl = ""
    return tgl

def ctanggal_polos(tanggal) :
    if tanggal :
        tgl = datetime.strptime(str(tanggal), '%Y-%m-%d').strftime('%Y%m%d')
    else :
        tgl = ""
    return tgl

def ctanggalwaktu_polos(tanggal) :
    if tanggal :
        tz = pytz.timezone('Asia/Jakarta')
        # tgl = datetime.strptime(str(tanggal), '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
        tgl = datetime.strftime(pytz.utc.localize(datetime.strptime(str(tanggal),'%Y-%m-%d %H:%M:%S')).astimezone(tz),"%Y%m%d%H%M%S") 
    else :
        tgl = ""
    return tgl


def update_hdr_pungut(self,cn_id,pungutan,jum) :
    if jum > 0 :
        hdr = self.env['dps.header.pungutan'].search([('cn_id','=',cn_id.id),('kode_pungutan_id.uraian','=',pungutan)], limit=1)
        # print(hdr.id)
        if hdr :
            hdr.write({'nilai_pungutan': jum })
            # print('wwwwk')

def count_pungut(self,cn_id,pungutan) :
    barang = cn_id.barang_ids
    result = 0
    if barang :
        for bar in barang :
            det = self.env['dps.detail.pungutan'].search([('barang_id','=',bar.id),('kode_pungutan_id.uraian','=',pungutan)])
            if det :
                for t in det :
                    result = result + t.nilai_pungutan 
                    print(t.nilai_pungutan)       
        update_hdr_pungut(self,cn_id,pungutan,result)   

def jprint(obj):
        # create a formatted string of the Python JSON object
        text = json.dumps(obj, sort_keys=True, indent=4)
        print(text) 

def update_pungut(self,cn) :
    cn_data = self.env['dps.cn.pibk'].sudo().search([('id','=',cn.id)])
    if cn_data :
        kurs = cn_data.ndpbm
        if kurs > 0 :
            pungut = {
                'BM' : 0,
                'PPN' : 0,
                'PPH' : 0
            }
            barang_ids = cn.barang_ids
            if barang_ids :
                for barang in barang_ids :
                    cif = barang.cif
                    if cif > 0 :
                        det_pungut = barang.detail_pungutan_ids
                        if det_pungut and not barang.flag_bebas :
                            for det in det_pungut :
                                det.nilai_pungutan = round_thousand(cif * kurs * det.tarif / 100) 
                                for x, y in pungut.items():
                                    if x == det.kode_pungutan_id.uraian :
                                        # y += det.nilai_pungutan
                                        pungut[x] += det.nilai_pungutan
                                        # print(y)
                # print(pungut['BM'])
            for  x, y in pungut.items():
                pung = self.env['dps.header.pungutan'].sudo().search([('cn_id','=',cn.id),('kode_pungutan_id.uraian','=', x)])
                if pung :
                    pung.nilai_pungutan = y

def dateParser(date, origin_format, target_format):
    if date:
        return datetime.strptime(date, origin_format).strftime(target_format)
    else:
        return ""