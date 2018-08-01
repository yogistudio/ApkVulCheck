import os
import sys
import xml.dom.minidom
import re
import zipfile
#resultinfo={"xss":[item1,item2]},{}}  item={"path":"path","line":"line","linecode":"linecode"}
resultinfo={}

#
#banner_begin
#
def banner_bigin():
	print(" "*45+"#"*10+"#"*45)
	print(" "*44+"#"+" "*3+"死"+" "+"不"+" "*2+"#"+" "*43+"#")
	print(" "*43+"#"+" "*4+"生"+" "+"服"+" "*3+"#"+" "*42+"#")
	print(" "*42+"#"+" "*5+"看"+" "+"就"+" "*4+"#"+" "*41+"#")	
	print(" "*41+"#"+" "*6+"淡"+" "+"干"+" "*5+"#"+" "*40+"#")
	print("#"*40+"开始输出白盒扫描结果"+"#"*40)
	print(" "*40+"#powered by zsdlove#"+" "*39+"#")
	print(" "*41+"#"+" "*6+"影"+" "+"实"+" "*5+"#"+" "*40+"#")
	print(" "*42+"#"+" "*5+"武"+" "+"验"+" "*4+"#"+" "*41+"#")
	print(" "*43+"#"+" "*4+"者"+" "+"室"+" "*3+"#"+" "*42+"#")
	print(" "*44+"#"*12+"#"*44)
#
#banner_end
#
def banner_finished():
	print(" "*84+"#"+"#"*15)
	print(" "*84+"#"+" "*3)
	print("#"*84+"#"*5+"#结束#"+"#"*5)
	print(" "*84+"#"+" "*3)
	print(" "*84+"#"+"#"*15)
	
#
#从conf.xml文件中获取特征值
#	
def getFeatureFromXml():
	vulhub={}
	dom = xml.dom.minidom.parse('lib/conf.xml')
	root = dom.documentElement
	nodelist=root.childNodes
	for node in nodelist:
		if node.nodeName!="#text":
			#print(node.nodeName)
			vulname=node.nodeName
			for nd in node.childNodes:
				if nd.nodeName!="#text" and nd.nodeName!="desc":
					#print(nd.firstChild.data)
					feature=nd.firstChild.data
					if vulname not in vulhub.keys():
						vulhub[vulname]={}
					if 'item' not in vulhub[vulname].keys():
						vulhub[vulname]['item']=[]
					vulhub[vulname]['item'].append(feature)
				elif nd.nodeName=="desc":
					if vulname not in vulhub.keys():
						vulhub[vulname]={}
					if 'item' not in vulhub[vulname].keys():
						vulhub[vulname]['item']=[]
					vulhub[vulname]['desc']=nd.firstChild.data
				else:
					pass
	return vulhub
def VulScanEngine(path,apkfilename):
	apkfilename=os.getcwd()+'//report//'+apkfilename
	os.makedirs(apkfilename)
	resultfile=open(apkfilename+"//_result.html",'w+')
	resultfile2=open(apkfilename+"//_result.txt",'w+')
	features=getFeatureFromXml()
	print("开始进dex反编译")
	decompiledex()
	print("开始进行AndroidManifest.xml反编译")
	decompile_AndroidManifest()
	print("开始进行安卓漏洞静态扫描")
	for root,dirs,files,in os.walk(path):
			for file in files:
				if os.path.splitext(file)[1] == '.smali':
					refs={}
					#print(os.path.join(root,file))
					filepath=os.path.join(root,file)
					className=os.path.splitext(file)[0]
					print("开始扫描类文件："+filepath)
					f=open(filepath,'rb')
					lines=f.readlines()
					lineslen=len(lines)
					className=os.path.splitext(file)[0]
					try:
						while lineslen>0:
								lineslen=lineslen-1
								linecode=lines[lineslen]
								linecode=str(linecode,encoding="utf-8")	
								for vulname in features.keys():
									for feature in features[vulname]['item']:
										m=re.match(r'.*'+feature+'.*',linecode)
										if m:
											print("[+]找到疑似"+vulname+"漏洞点，地址是："+filepath)
											vulinfo={}
											vulinfo["path"]=filepath
											vulinfo["linecode"]=linecode
											vulinfo["line"]=str(lineslen)
											if vulname not in resultinfo.keys():
												resultinfo[vulname]=[]
											resultinfo[vulname].append(vulinfo)
											resultfile2.write("[+]checked:"+vulname+" 地址："+filepath+"行数："+str(lineslen)+"\n")
										else:
											pass
									
					except:
						pass
	banner_bigin()
	resultfile.write("<h2>白盒扫描漏洞报告</h2>")
	for vul in resultinfo.keys():
		resultfile.write("<div id='menu'><h3><a href=#"+vul+">"+vul+"漏洞</a></h3>")
	for vul in resultinfo.keys():
		resultfile.write("<div id="+vul+"><h3>"+vul+"漏洞</h3><a href='#menu'><h3>  返回漏洞目录</h3><a>")
		count=0
		for vulitem in resultinfo[vul]:
			count=count+1
			print("[+]找到疑似"+vul+"漏洞点！")
			print("代码是："+vulitem["linecode"].strip())
			print("行数："+vulitem["line"])
			print("路径："+vulitem["path"])
			resultfile.write("<h4>第"+str(count)+"处漏洞点</h4>")
			resultfile.write("<p>代码是："+vulitem["linecode"].strip()+"</p>")
			resultfile.write("<p>行数："+vulitem["line"]+"</p>")
			resultfile.write("<p>路径："+vulitem["path"]+"</p>")
			resultfile.write("</div>")
	banner_finished()
	input("按任意键结束");
	
#
#获得apk文件名
#

def getapkFileName():
	apkfilenamelist=[]
	for root,dirs,files,in os.walk('workspace'):
			for file in files:
				if os.path.splitext(file)[1] == '.apk':
					filepath=os.path.join(root,file)
					filepath=filepath.split('.')[0].split('\\')[-1]
					apkfilenamelist.append(filepath)
	return apkfilenamelist
	
#
#对classes.dex文件进行反编译，获得smali文件
#

def decompiledex():
	path=os.getcwd()+'//workspace//result//'
	apkfileNames=getapkFileName()
	getdexfile()#处理apk文件
	for apkfileName in apkfileNames:
		cmd="java -jar lib/baksmali.jar -o workspace/result/"+apkfileName+" workspace/result/"+apkfileName+"/classes.dex"
		os.system(cmd)
	print('dex文件反编译成功')
	
#
#对androidManifest.xml进行反编译，获得明文文件
#

def decompile_AndroidManifest():
	path=os.getcwd()+'//workspace//result//'
	apkfileNames=getapkFileName()
	getAndroidManifest()#获取apk中的AndroidManifest.xml文件
	for apkfileName in apkfileNames:
		cmd="java -jar lib/AXMLPrinter2.jar workspace/result/"+apkfileName+"/AndroidManifest.xml > "+" workspace/result/"+apkfileName+"/AndroidManifest2.xml"
		print("打印cmd"+cmd)
		os.system(cmd)
		android_manifest_read("workspace/result/"+apkfileName+"/AndroidManifest2.xml")
	print('AndroidManifest.xml反编译成功！')
	
#
#从获得apk文件路径
#

def getApkFilePath():
	apkfilelist=[]
	for root,dirs,files,in os.walk('workspace'):
			for file in files:
				if os.path.splitext(file)[1] == '.apk':
					filepath=os.path.join(root,file)
					apkfilelist.append(filepath)
	return apkfilelist
	
#
#获得dex文件
#

def getdexfile():
	apkfilelist=getApkFilePath()
	print('py文件目录'+os.getcwd())
	for apkfilepath in apkfilelist:
		try:
			zipfiles=zipfile.ZipFile(apkfilepath)
			a=zipfiles.read('classes.dex')
			if a !='':
				apkfileName=apkfilepath.split('.')[0].split('\\')[-1]
				print('apk文件名'+apkfileName)
				apkdir=os.getcwd()+'\\workspace\\result\\'+apkfileName
				print(apkdir)
				if not os.path.exists(apkdir):
					os.makedirs(apkdir)
				dexfile=open('workspace/result/'+apkfileName+'/classes.dex','wb')
				dexfile.write(a)
				print('获取classes.dex文件成功')
			else:
				print('找不到classes.dex文件！')
		except:
			continue
#
#获取manifest.xml文件
#			
def getAndroidManifest():
	apkfilelist=getApkFilePath()
	print('py文件目录'+os.getcwd())
	for apkfilepath in apkfilelist:
		try:
			zipfiles=zipfile.ZipFile(apkfilepath)
			a=zipfiles.read('AndroidManifest.xml')
			if a !='':
				apkfileName=apkfilepath.split('.')[0].split('\\')[-1]
				print('apk文件名'+apkfileName)
				apkdir=os.getcwd()+'\\workspace\\result\\'+apkfileName
				print(apkdir)
				if not os.path.exists(apkdir):
					os.makedirs(apkdir)
				dexfile=open('workspace/result/'+apkfileName+'/AndroidManifest.xml','wb')
				dexfile.write(a)
				print('获取AndroidManifest.xml文件成功')
			else:
				print('找不到AndroidManifest.xml文件！')
		except:
			continue

#
#manifest.xml解析结果保存,数据结构定义
#result_manifest={'packageName':'','UsesPermission':[],'Permission':[],'application':{'backup':'','activity':{},'service':'{},'receiver':{},'provider':{}}}
#

result_manifest={}
			
#
#解析xml文件
#

def android_manifest_read(path):
	#try:
		dom = xml.dom.minidom.parse(path)
		print("xml读取成功")
		root = dom.documentElement
		packageName=getPackageName(root)
		print("apk包名是："+packageName)
		nodelist=root.childNodes
		for node in nodelist:
			if node.nodeName!="#text":
				#print(node.nodeName)
				getUsesPermission(node)#usespermission
				getPermission(node)#permission
				print('开始打印子节点')
				applicationtab(node)
	#except:
	#	pass
#
#解析application标签,检查bakup备份
#

def applicationtab(node):
	if node.nodeName == "application":
		print("allowBackup："+node.getAttribute('android:allowBackup'))
		if node.getAttribute('android:allowBackup')=="true":
			print("存在任意数据备份漏洞")
		else:
			print("不存在任意数据备份漏洞")
		for cn in node.childNodes:
				if cn.nodeName!="#text":
					decompile_service(cn)
					decompile_receiver(cn)
					decompile_receiver(cn)
					decompile_provider(cn)
				else:
					pass
					
	else:
		pass
#
#解析activity,cn是节点
#

def decompile_activity(cn):
	if cn.nodeName=="activity":
		print("exported:"+cn.getAttribute("android:exported"))
		if cn.getAttribute("android:exported")=="true":
			print("activity组件导出,存在风险")
		else:
			print("activity组件安全")
	else:
		pass
	return cn.getAttribute("android:exported")
#
#解析service
#
def decompile_service(cn):
	if cn.nodeName=="service":
		print("exported:"+cn.getAttribute("android:exported"))
		if cn.getAttribute("android:exported")=="true":
			print("service组件导出,存在风险")
		else:
			print("service组件安全")
	else:
		pass
	return cn.getAttribute("android:exported")
	
#
#解析receiver
#

def decompile_receiver(cn):
	if cn.nodeName=="receiver":
		print("exported:"+cn.getAttribute("android:exported"))
		if cn.getAttribute("android:exported")=="true":
			print("receiver组件导出,存在风险")
		else:
			print("receiver组件安全")
	else:
		pass
	return cn.getAttribute("android:exported")
	
#
#解析provider
#

def decompile_provider(cn):
	if cn.nodeName=="provider":
		print("exported:"+cn.getAttribute("android:exported"))
		if cn.getAttribute("android:exported")=="true":
			print("provider组件导出,存在风险")
		else:
			print("provider组件安全")
	else:
		pass
	return cn.getAttribute("android:exported")
#
#获得apk包名
#

def getPackageName(root):
	packageName=root.getAttribute('package')
	return packageName
#
#获得应用运行权限
#

def getUsesPermission(node):
	if node.nodeName == "uses-permission":
		print("申请的权限名为："+node.getAttribute('android:name'))
	return node.getAttribute('android:name')

#
#获得应用自定义权限：权限名，保护级别
#

def getPermission(node):
	if node.nodeName == "permission":
		print("自定义权限名："+node.getAttribute('android:name'))
		print("保护级别为："+node.getAttribute('android:protectionLevel'))
	return node.getAttribute('android:name')
	
if __name__ == '__main__':
	decompile_AndroidManifest()
	#apkfilenames=getapkFileName()
	#for apkfilename in apkfilenames:
	#	path='./workspace/result/'+apkfilename
	#	VulScanEngine(path,apkfilename)
	android_manifest_read("C:/Users/74728/Desktop/ApkCodeCheck/workspace/result/test/AndroidManifest2.xml")
	
	
	