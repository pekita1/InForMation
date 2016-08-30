#!coding=utf-8
'''
脚本功能:
1.收集windows系统信息
2.收集windows下中间件日志
3.全盘搜索windows日志
'''
import os
import re
import sys
import shutil
import threading
import time
import psutil
import datetime
import optparse

class logs:
	def __init__(self):
		self.result=os.popen('wmic process get ExecutablePath').readlines()  #获取进程信息命令
		self.a_res=r'([^"]*)bin\\httpd.exe'   #寻找apache日志
		self.a2_res=r'CustomLog (.*) common'

		self.run()

	def run(self):  #多线程运行
		print '----------------------------------------'
		print u'开始收集中间件日志.....'
		print ''
		threading.Thread(target=self.find_apache).start()
		threading.Thread(target=self.find_iis).start()
		threading.Thread(target=self.find_jboss).start()
		threading.Thread(target=self.find_nginx).start()
		threading.Thread(target=self.find_tomcat).start()
		threading.Thread(target=self.find_weblogic).start()
		
			
	def find_apache(self):  #寻找并copy apache日志文件
		tag=0
		for i in self.result:
			if tag==0:
				p=re.compile(self.a_res)
				L=p.findall(i)

				if len(L)>0:
					print u'该服务器中间件为 Apache'
					tag=1
					paths=os.path.join(L[0],"conf\httpd.conf")   #寻找apache配置文件

					f=open(paths).readlines()

					for i in f:
						p2=re.compile(self.a2_res)                   #在配置文件中寻找日志存放路径
						L2=p2.findall(i)
						if len(L2)>0:
							pathdir=os.path.dirname(L2[0].replace('"',''))
							if os.path.exists(pathdir):
								try:
									shutil.copytree(pathdir,'.\Apache_logs')
								except:
									shutil.rmtree('.\Apache_logs')
									shutil.copytree(pathdir,'.\Apache_logs')
								print 'Copy Apache_Logs success'
								break
							else:
								print u'Apache Logs_path error'
						else:
							pass
				else:
					pass
			else:
				break


	def find_iis(self):
		#p1="C:\WINNT\system32\inetsrv\MetaBase.bin"      #IIS5.0配置文件
		p2="C:\WINDOWS\system32\inetsrv\MetaBase.xml"    #IIS6.0配置文件
		p3="C:\Windows\System32\inetsrv\config\applicationHost.config"  #IIS7.0配置文件
		i6_res=r'LogFileDirectory="([^"]*)"'
		i7_res=r'logFile logFormat="W3C" directory="([^"]*)"'
		
		if os.path.exists(p2):
			self.find_iis_f(p2,i6_res,'.\IIS6.0_logs')
		else:
			self.find_iis_h('C:\WINDOWS\system32\LogFiles','.\IIS6.0_logs')

		if os.path.isfile(p3):
			self.find_iis_f(p3,i7_res,'.\IIS7.0_logs')
		else:
			self.find_iis_h('C:\inetpub\logs\LogFiles','.\IIS7.0_logs')

	def find_iis_h(self,oldpath,newpath):          #直接判断默认日志路径是否存在
		try:
			if os.path.exists(oldpath):
				try:
					shutil.copytree(oldpath,newpath)
				except:
					shutil.rmtree(newpath)
					try:
						shutil.copytree(oldpath,newpath)
					except:
						pass
				#print 'Copy IIS_Logs success'
			else:
				pass
		except:
			pass

	def find_iis_f(self,pathdir,res,newpath):      #判断配置文件是否存在
		print u'该服务器中间件为 IIS'
		f=open(pathdir).readlines()
		for i in f:
			p2=re.compile(res)                
			L2=p2.findall(i)
							
			if len(L2)>0:
				pathdir=L2[0]
				if "%SystemDrive%" in pathdir:
					c=os.getenv("SystemDrive")
					pathdir.replace('%SystemDrive%',c)
					
				#print pathdir

				if os.path.exists(pathdir):
					try:
						shutil.copytree(pathdir,newpath)
					except:
						shutil.rmtree(newpath)
						shutil.copytree(pathdir,newpath)
					print 'Copy IIS_Logs success'
					break
				else:
					print u'IIS Logs_path error'
			else:
				pass

	def find_jboss(self):   #判断jboss中间件日志
		try:
			jbossenv = os.environ["JBOSS_HOME"]
			jbosspath=os.path.join(jbossenv,'standalone/log')
			
			if os.path.isdir(jbosspath):
				print u"该服务器中间件为 JBOSS"
				try:
					shutil.copytree(jbosspath,"./JBOSS_logs")
				except:
					shutil.rmtree("./JBOSS_logs")
					shutil.copytree(jbosspath,"./JBOSS_logs")
				print 'Copy Jboss_Logs success'
		except:
			pass
			
	def find_nginx(self):
		#print 'nginx'
		pass

	def find_tomcat(self):
		try:
			r=os.popen("wmic process get commandline").read()
			res=r'([^"]*Tomcat[^\\]*\\)'
			p=re.compile(res)
			L=p.findall(r)
			print L
			if len(L)>0:
				print u"该服务器中间件为 Tomcat"
				to_path=os.path.join(L[0],"./logs")
				try:
					shutil.copytree(to_path,"./Tomcat_logs")
					print 'Copy Tomcat_Logs success'
				except:
					try:
						shutil.rmtree("./Tomcat_logs")
						shutil.copytree(to_path,"./Tomcat_logs")
						print 'Copy Tomcat_Logs success'
					except:
						#print to_path
						os.system("xcopy "+to_path+" ./Tomcat_logs")
						#print 'Copy Tomcat_Logs success'
		except:
			pass

	def find_weblogic(self):
		#print 'weblogic'
		pass



class informations:
	def __init__(self):
		self.run()
		pass

	def run(self):
		print '----------------------------------------'
		print u'开始获取系统信息......'
		print ''
		if os.path.exists("./Informations"):
			pass
		else:
			os.mkdir("./Informations")

		self.ip_mac()             #获取系统ip/mac地址
		self.kj_time()            #获取开机时间
		self.users()              #获取用户信息
		self.os_version()         #获取系统信息，以及补丁
		self.tasklist()           #获取进程信息
		self.hosts()              #获取hosts文件信息
		self.os_logs()           #获取系统日志
		self.netstat()            #获取网络连接信息


	def kj_time(self):
		try:
			time=datetime.datetime.fromtimestamp(psutil.boot_time ()).strftime("%Y-%m-%d %H: %M: %S")
			f=open("./Informations/kj_time.txt",'w')
			f.write(time)
			f.close()
			print u'开机时间：获取Success！'
		except:
			print u'开机时间：获取Error！'

	def ip_mac(self):
		try:
			ip_mac=os.popen("ipconfig /all").read()
			f=open("./Informations/ip_mac.txt",'w')
			f.write(ip_mac)
			f.close()
			print u'IP_MAC: 获取Success！'
		except:
			print u'IP_MAC: 获取Error！'

	def users(self):
		try:
			users=os.popen("net user").read()
			f=open("./Informations/users.txt",'w')
			f.write(users)
			f.close()
			print u'用户信息: 获取Success！'
		except:
			print u'用户信息: 获取Error！'

	def os_version(self):
		try:
			os_version=os.popen("systeminfo").read()
			f=open("./Informations/systeminfo.txt",'w')
			f.write(os_version)
			f.close()
			print u'操作系统版本: 获取Success！'
		except:
			print u'操作系统版本: 获取Error！'

	def tasklist(self):
		try:
			tasklist=os.popen("tasklist").read()
			f=open("./Informations/tasklist.txt",'w')
			f.write(tasklist)
			f.close()
			print u'进程信息: 获取Success！'
		except:
			print u'进程信息: 获取Error！'

	def hosts(self):
		paths="c:\windows\system32\drivers\etc\hosts"
		if os.path.exists(paths):
			try:
				shutil.copy(paths,"./Informations/hosts.txt")
			except:
				os.remove("./Informations/hosts.txt")
				shutil.copy(paths,"./Informations/hosts.txt")
			print u'hosts文件: 获取Success！'
		else:
			print u'hosts文件：获取Error！'

	def os_logs(self):
		# if os.path.exists("./os_logs"):
		# 	pass
		# else:
		# 	os.mkdir("./os_logs")
		# try:
		# 	logs_name=os.popen("wevtutil el").readlines()
		# 	for i in logs_name:
		# 		i=i.replace('\n','').replace('/','%4')                     #只能导出一部分系统日志
		# 		os.popen("wevtutil epl "+i+" ./os_logs/"+i+".evtx")

		# 	print u'系统日志： 获取Success！'
		# except:
		# 	print u'系统日志： 获取Error！'
		paths=os.getcwd()
		lists=["wmic nteventlog where filename='application' backupeventlog "+paths+"\\application.evt",
		"wmic nteventlog where filename='security' backupeventlog "+paths+"\security.evt",
		"wmic nteventlog where filename='system' backupeventlog "+paths+"\system.evt"]
		for i in lists:
			os.popen(i)


	def netstat(self):
		try:
			netstat=os.popen("netstat -anob").read()
			if len(netstat)<50:    #执行上面一条权限不够的情况下
				netstat=os.popen("netstat -ano").read()
			f=open("./Informations/netstat.txt",'w')
			f.write(netstat)
			f.close()
			print u'服务连接信息：获取Success！'
		except:
			print u'服务连接信息：获取Error！'



class search_logs:
	def __init__(self):
		self.path=os.getcwd()
		self.run()
		pass

	def run(self):
		print '----------------------------------------'
		print u'开始搜索.log文件....'
		print ''
		paths=raw_input(unicode('请输入磁盘符(缺省为全盘),如(C:/),输入(exit)则退出:','utf-8').encode('gbk'))
		if paths=="":
			self.dir()
		elif paths=="exit":
			sys.exit(1)
		else:
			self.dir_(paths)
		print u"搜索完毕！"

	def dir_(self,paths):            #单独一个盘搜索

		self.search(paths)

	def dir(self):
		a=os.popen("wmic VOLUME GET Name").read()        #全盘搜索
		b=a.replace("\r","").strip().split("\n")
		for i in b[1:]:
			paths=i.strip()
			self.search(paths)

	def search(self,paths):
		try:
			if os.path.isdir(paths):  #如果是目录
				files=os.listdir(paths)  #列出目录中所有的文件
				for i in files:
					i=os.path.join(paths,i)  #构造文件路径
					self.search(i)           #递归
			elif os.path.isfile(paths): #如果是文件
				f=os.path.splitext(paths)   #输出文件后缀为txt的文件名称
				if f[1]==".log":
					print paths
					a=os.path.splitdrive(paths)[1]
					b=os.path.split(a)[0]
					c=os.path.join("./logs_files/",b[1:])  #构造新的路径
					d=os.path.join("./logs_files/",a[1:])  #构造新的路径
					if os.path.isdir(c):
						shutil.copy(paths,d)
					else:
						os.makedirs(c)
						shutil.copy(paths,d)
			else:
				#print u'路径不存在'
				pass
		except Exception,e:
			#print e
			pass


class main_:
	def __init__(self):
		self.run()

	def helps(self):
		print u"例子：\>	get_information.exe -i start -L start -s start  #运行所有功能"
		print u"例子：\>	get_information.exe -i start  #运行收集系统信息功能"
		print u""
		self.option=optparse.OptionParser()
		self.option.add_option('-i','--information', default=False,help=u'获取系统信息')
		self.option.add_option('-L','--log', default=False,help=u'获取中间件日志')
		self.option.add_option('-s','--search',default=False,help=u'搜索日志文件')	
		self.options,arg=self.option.parse_args()	
		return self.options

	def run(self):
		self.helps()
		if self.options.information or self.options.log or self.options.search:
			if self.options.information:
				try:
					informations()       #获取系统信息
				except:
					pass
			if self.options.log:
				try:
					logs()               #获取中间件日志
				except:
					pass
			time.sleep(2)
			if self.options.search:
				try:
					search_logs()        #搜索日志t:
				except:
					pass
		else:
			self.option.print_help()

if __name__=="__main__":
	main_()
