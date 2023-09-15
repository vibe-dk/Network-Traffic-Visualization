import dpkt
import socket
import pygeoip
import requests

#file_path="GeoLiteCity/GeoLiteCity.dat"
gi=pygeoip.GeoIP('GeoLiteCity.dat')

def get_publicIP():
    response=requests.get('https://api.ipify.org?format=json')
    ip=response.json()['ip']
    return ip


def geoloc(dstip,srcip,publicIP):
    dst=gi.record_by_name(dstip)
    src=gi.record_by_name(str(publicIP))
    try:
        dst_long=dst['longitude']
        dst_lati=dst['latitude']
        src_long=src['longitude']
        src_lati=src['latitude']
        kml=(
            '<Placemark>\n'
            '<name>%s</name>\n'
            '<extrude>l</extrude>\n'
            '<tessellate>l</tessellate>\n'
            '<styleUrl>#transBluePoly</styleUrl>\n'
            '<LineString>\n'
            '<coordinates>%6f,%6f\n%6f,%6f</coordinates>\n'
            '</LineString>\n'
            '</Placemark>\n'            
        )%(dstip, dst_long, dst_lati, src_long, src_lati)
        
        return kml
    
    except:
        return ''
    

def plot(pcap,publicIP):
    kmlpts=''
    for(ts,buf) in pcap:
        try:
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            ''' wifi = dpkt.ieee80211.Dot11(buf)
            ip = wifi.data'''
            src=socket.inet_ntoa(ip.src)
            dst=socket.inet_ntoa(ip.dst)
            kml=geoloc(dst,src,publicIP)
            kmlpts=kmlpts+kml
        except:
            pass
    return kmlpts


def main():
    f=open('packets.pcap','rb')
    pcap=dpkt.pcap.Reader(f)
    publicIP=get_publicIP()
    kmlheader='<?xml version="1.0" encoding="UTF-8"?> \n <kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n'\
    '<Style id="transBlueploly">\n'\
                '<LineStyle>\n'\
                '<width>1.5</width>\n'\
                '</LineStyle>\n'\
                '</Style>'
    kmlfooter='</Document>\n</kml>\n'
    kmldoc=kmlheader+plot(pcap,publicIP)+kmlfooter
    #print(kmldoc)
    with open('sample.kml','w') as f:
        for data in kmldoc:
            f.write(data)

    print('.....FILE CREATED.....')


if __name__=='__main__':
    main()
