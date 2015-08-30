
import json
import libvirt
import random
import sqlite3
import uuid
import re
from BeautifulSoup import BeautifulSoup
from flask import Flask, render_template
from flask import request
from flask import jsonify

app = Flask(__name__)


@app.route('/')
def index():
  return render_template('index.html')
#######       VM APIs         ###########
@app.route('/vm/create/')
def create():
    vmName = request.args.get('name')
    print vmName
    instance_type = request.args.get('instance_type')
    instance_type = int(instance_type)
    success = 0
    ##### Connect to Database and create table if table is not created      ######
    conn = sqlite3.connect('orchestration1.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE if not exists resource(pmid integer, vmid text, instance_type integer, memory integer, cpu integer, name text)''')
    
    requestMemory = json_object['types'][instance_type-1]['ram']
    requestCPU = json_object['types'][instance_type-1]['cpu']
    requestMemory = int(requestMemory)
    requestCPU = int(requestCPU)
    loop=0
    for ip in ipAddress:
    	print "loop entry "
        cmd = 'qemu+tcp://' + ip + '/system'
        connection = libvirt.open(cmd)
        p=connection.getCapabilities()
        soup = BeautifulSoup(p)
        a = soup.find('cpus')
        totalCPU = a['num']
        totalCPU = int(totalCPU)
        totalMemory = soup.find('memory').string
        totalMemory = int(totalMemory) /1024
        freeMemory = connection.getFreeMemory()/(1024*1024)
        freeMemory = int(freeMemory)
        print "Outside Loop"
        print freeMemory
        allocatedCPU = 0
        allocatedMemory =0
        c.execute("SELECT * from resource where pmid = ?",(loop,))
        for record in c.fetchall():
            allocatedCPU = allocatedCPU + record[4]
        
        if requestCPU <= (totalCPU- allocatedCPU) and requestMemory <= (freeMemory):
            print "Inside loop"
            print allocatedCPU
            print freeMemory
            f = open('vm.xml', 'r+')
            text = f.read()
            name = vmName
            name = '<name>' + name + '</name>'
            text = re.sub('<name>.*</name>',name , text)

            newuu = uuid.uuid1()
            newuu = '<uuid>'+ str(newuu) +'</uuid>'
            text = re.sub('<uuid>.*</uuid>',newuu , text)
            
            requestMem = requestMemory * 1024
            memreplace = '<memory unit=\'KiB\'>' +str(requestMem) +'</memory>'
            text = re.sub('<memory unit=\'KiB\'>.*</memory>',memreplace , text)


            memreplace = '<currentMemory unit=\'KiB\'>'+ str(requestMem) +'</currentMemory>'
            text = re.sub('<currentMemory unit=\'KiB\'>.*</currentMemory>',memreplace,text)

            cpureplace = '<vcpu placement=\'static\'>' + str(requestCPU)+ '</vcpu>'
            text = re.sub('<vcpu placement=\'static\'>.*</vcpu>',cpureplace,text)

            imageFilePathReplace = "\'" + imageFilePath + "\'"
            sourceReplace = '<source file=' + imageFilePathReplace +  '/>'
            text = re.sub('<source file=.*/>',sourceReplace,text)

            f.seek(0)
            f.write(text)
            f.truncate()
            f.close()
            xml = ""
            with open("vm.xml", "r") as file:  
                xml = file.read()
            connection.defineXML(xml)
            startVM = connection.lookupByName(vmName)
            startVM.create()
            vmidRandom = random.randint(1,50000)
            c.execute("INSERT INTO resource VALUES (?,?,?,?,?,?)",(loop,vmidRandom,instance_type,requestMemory,requestCPU,vmName) )		
            conn.commit()
            return str(vmidRandom)
        # connection.close()
        loop+=1    
        print "Exit loop"


	return '-1'

@app.route('/pm/pmid/listvms/')
def listvms():
    pmidSearch = request.args.get('pmid')
    conn = sqlite3.connect('orchestration1.db')
    c = conn.cursor()
    c.execute("SELECT vmid from resource where pmid = ?",(pmidSearch,))
    return jsonify(vmids=c.fetchall())



@app.route('/vm/types/')
def vmtypes():   
    return jsonify(Displaying_Types=json_object)

@app.route('/pm/list/')
def pmlist():
	l=[]
	for lo in range(len(ipAddress)):
		l.append(lo)
	return jsonify(pmids=l)

@app.route('/vm/query/')
def vmquery():
	vm_id = request.args.get('vmid')
	conn = sqlite3.connect('orchestration1.db')
	c = conn.cursor()
	c.execute("SELECT vmid,name,instance_type,pmid from resource where vmid = ?",(vm_id,))
	dict = {}
	for record in c.fetchall():
		dict['vmid']=record[0]
		dict['name']=record[1]
		dict['instance_type']=record[2]
		dict['pmid']=record[3]
	return jsonify(dict)
@app.route('/vm/destroy/')
def vmdestroy():
	vm_id = request.args.get('vmid')
	vm_id=int(vm_id)
	conn = sqlite3.connect('orchestration1.db')
	c = conn.cursor()
	c.execute("SELECT pmid from resource where vmid = ?",(vm_id,))
	tempvar=c.fetchone()[0]
	tempvar=int(tempvar)
	cmd = 'qemu+tcp://' + ipAddress[tempvar] + '/system'
	connection = libvirt.open(cmd)
	c.execute("SELECT name from resource where vmid = ?",(vm_id,))
	temvar=c.fetchone()[0]
	startVM = connection.lookupByName(temvar)
	startVM.destroy()
	c.execute("DELETE  from resource where vmid = ?",(vm_id,))
	conn.commit()
	return "1"

@app.route('/pm/pmid/')
def pmquery():
    pmidSearch = request.args.get('pmid')
    pmidSearch = int(pmidSearch)
    conn = sqlite3.connect('orchestration1.db')
    c = conn.cursor()
    ip = ipAddress[int(pmidSearch)]
    cmd = 'qemu+tcp://' + ip + '/system'
    connection = libvirt.open(cmd)
    p=connection.getCapabilities()
    soup = BeautifulSoup(p)
    a = soup.find('cpus')
    totalCPU = a['num']
    totalCPU = int(totalCPU)
    totalMemory = soup.find('memory').string
    totalMemory = int(totalMemory) /1024
    freeMemory = connection.getFreeMemory()/(1024*1024)
    freeMemory = int(freeMemory)
    result = {}
    result['pmid'] = pmidSearch
    temp1 = {'cpu':totalCPU,'ram':totalMemory}
    result['capacity'] = temp1
    
    allocatedCPU = 0
    c.execute("SELECT * from resource where pmid = ?",(pmidSearch,))
    counter =0
    for record in c.fetchall():
        allocatedCPU = allocatedCPU + record[4]
        counter = counter + 1

    allocatedCPU = totalCPU - allocatedCPU
    temp2 = {'cpu':allocatedCPU,'ram':freeMemory}
    result['free'] = temp2
    print counter
    result['vms'] = counter
    return jsonify(result)


if __name__ == '__main__':
	
	###### Reading all physical addresses into array ######

    with open("pm_file.txt") as f:
        ipAddress = f.readlines()

    index=0
    for i in ipAddress:
    	ipAddress[index] = ipAddress[index].rstrip()
    	index+=1

    print ipAddress

    ###### Reading json file ######

    with open("json_file.json") as json_file:
        json_object = json.load(json_file)
    imageFilePath = '/var/lib/libvirt/images/ubuntu.img'
    app.run(host='10.1.132.148',debug=True)