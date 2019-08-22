#!/usr/bin/python
# -*- coding: UTF-8 -*-
from xml.dom.minidom import parse
import xml.dom.minidom

class PDMHandler(object):
  PKG_ATTR_LIST    = ["Name","Code","CreationDate","Creator","ModificationDate","Modifier"]
  TBL_ATTR_LIST    = ["Name","Code","CreationDate","Creator","ModificationDate","Modifier",
                      "PhysicalOptions"]
  """COL_ATTR_LIST    = ["Name","Code","CreationDate","Creator","ModificationDate","Modifier",
                      "DataType","Length","Column.Mandatory","Comment"]"""
  COL_ATTR_LIST    = ["Name","Code","DataType","Length","Column.Mandatory","Comment"]				 
  IDX_ATTR_LIST    = ["Name","Code","CreationDate","Creator","ModificationDate","Modifier",
                      "PhysicalOptions","Unique"]
  IDXCOL_ATTR_LIST = ["CreationDate","Creator","ModificationDate","Modifier"]
  def __init__(self):
    return

  @staticmethod
  def parse(pdmfilename):
    """
    @brief       PDM文件导入函数    
    @param[in]   pdmfilename       pdm文件名
    @return      pdm文件的DOM结构
    """
    return xml.dom.minidom.parse(pdmfilename)

  @staticmethod
  def __get_nodes_by_path(parent,xml_path):
    """
    @brief 按路径取节点核心函数,通过传入一个节点和一个路径
           (类文件系统路径)的字符串,获得相应的子结点(或集合).
           例1: __get_nodes_by_path(node,"a/b/c|3/d")
             即获得node下a下b下第3个c节点下的所有d节点的一个
             list.
           例2: __get_nodes_by_path(node,"a/b/c|3/d|2")
             即获得node下a下b下第3个c节点下的第2个d节点.
             注意:此处返回的不是list,而是节点
    @param[in]   parent DOM中的父节点
    @return      节点list或节点句柄
    """
    curr_node = parent
    for tag in xml_path.split("/")[0:-1] :
      tag_desc = tag.split("|")
      tag_name,tag_index = tag_desc[0], ( int(tag_desc[1]) if len(tag_desc) == 2 else 0 )
      child_nodes = []
      for child_node in curr_node.childNodes :
        if child_node.nodeName == tag_name :
          child_nodes.append(child_node)
      if len(child_nodes) < tag_index + 1 :
        return []
      curr_node = child_nodes[tag_index]
    # -- 最后一级路径特殊处理 -- #
    tag = xml_path.split("/")[-1]
    tag_desc = tag.split("|")
    tag_name,tag_index = tag_desc[0], ( int(tag_desc[1]) if len(tag_desc) == 2 else None )
    child_nodes = []
    for child_node in curr_node.childNodes :
      if child_node.nodeName == tag_name :
        child_nodes.append(child_node)
    if tag_index == None :
      return child_nodes
    elif len(child_nodes) < tag_index + 1 :
      return []
    else :
      curr_node = child_nodes[tag_index]
      return curr_node

  @staticmethod
  def __get_attrs_by_list(parent,attr_list):
    """
    @brief       取PDM属性(注意:此属性非xml属性）
                 背景:PDM文件中主要节点(o:Table,o:Column...)的具体属性
                      一般以子节点形式表示，而不以通常的XML属性表示.此
                      函数传入一个attr_list,输出一个字典表示的:
                      { "attr":"value" ...}
    @param[in]   parent    需要被取属性的节点句柄
    @param[in]   attr_list 一个字符串的list["attr1","attr2"...],代表要取的属性名集合
    @return      返回一个dict:{"attr1":"value" ...}
    """
    ret_dict = {}
    for attr in attr_list :
      ret_dict[attr] = ""
      for child in parent.childNodes :
        if child.nodeName == "a:" + attr :
          ret_dict[attr] = child.childNodes[0].data
          break
    return ret_dict

  @staticmethod
  def __get_pkgnodes_recursively(o_pkg):
    #-- 需要传入一个o:Model/o:Package节点 --#
    if o_pkg.nodeName != "o:Model" and o_pkg.nodeName != "o:Package" :
      return []
    ret_list = []
    subpkgs = PDMHandler.__get_nodes_by_path(o_pkg,"c:Packages/o:Package")
    if subpkgs != None :
      for subpkg in subpkgs :
        ret_list.append(subpkg)
        ret_list = ret_list + PDMHandler.__get_pkgnodes_recursively(subpkg)
    else :
      return []
    return ret_list

  @staticmethod
  def getPkgNodes(hpdm):
    """
    @brief       获取pdm文件中所有的o:package的句柄list
    @param[in]   hpdm    待处理的pdm文件DOM句柄(可通过PDMHandler.parse取得)
    @return      返回pacakge的节点list:[pkg1,pkg2...],元素为DOM节点类型
    """
    ret_list = []
    try:
      o_mdl  = PDMHandler.__get_nodes_by_path(hpdm,"Model/o:RootObject/c:Children/o:Model")[0]
      ret_list.append(o_mdl)
    except IndexError:
      print ("ERROR:不是一个合法的pdm文件!")
      return []
    ret_list = ret_list + PDMHandler.__get_pkgnodes_recursively(o_mdl)
    return ret_list

  @staticmethod
  def getTblNodesInPkg(pkgnode):
    """
    @brief       获取指定o:Package下的所有o:Table的list
    @param[in]   pkgnode 待处理的o:Package节点(可通过PDMHandler.getPkgNodes取得)
    @return      返回o:Table的节点list:[tbl1,tbl2...],元素为DOM节点类型
    """
    return PDMHandler.__get_nodes_by_path(pkgnode, "c:Tables/o:Table")
  @staticmethod
  def getColNodesInTbl(tblnode):
    """
    @brief       获取指定o:Table下的所有o:Column的list
    @param[in]   tblnode 待处理的o:Table节点(可通过PDMHandler.getTblInPkg取得)
    @return      返回o:Column的节点list:[col1,col2...],元素为DOM节点类型
    """
    return PDMHandler.__get_nodes_by_path(tblnode, "c:Columns/o:Column")
  @staticmethod
  def getIdxNodesInTbl(tblnode):
    """
    @brief       获取指定o:Table下的所有o:Index的list
    @param[in]   tblnode 待处理的o:Table节点(可通过PDMHandler.getTblInPkg取得)
    @return      返回o:Index的节点list:[idx1,idx2...],元素为DOM节点类型
    """
    return PDMHandler.__get_nodes_by_path(tblnode, "c:Indexes/o:Index")
  @staticmethod
  def getIdxColNodesInIdx(idxnode):
    """
    @brief       获取指定o:Index下的所有o:IndexColumn的list
    @param[in]   idxnode 待处理的o:Index节点(可通过PDMHandler.getIdxNodesInTbl取得)
    @return      返回o:IndexColumn的节点list:[idxcol1,idxcol2...],元素为DOM节点类型
    """
    return PDMHandler.__get_nodes_by_path(idxnode,"c:IndexColumns/o:IndexColumn")

  @staticmethod
  def getPkgAttrs(pkgnode):
    """
    @brief       获取指定o:Package的属性(可取的属性参见PDMHandler.PKG_ATTR_LIST)
    @param[in]   pkgnode 待处理的o:Package节点(可通过PDMHandler.getPkgNodes取得)
    @return      返回一个字典dict:{"attr1":"value",...}
    """
    return PDMHandler.__get_attrs_by_list(pkgnode,PDMHandler.PKG_ATTR_LIST)
  @staticmethod
  def getTblAttrs(tblnode):
    """
    @brief       获取指定o:Table的属性(可取的属性参见PDMHandler.TBL_ATTR_LIST)
    @param[in]   tblnode 待处理的o:Table节点(可通过PDMHandler.getTblNodesInPkg取得)
    @return      返回一个字典dict:{"attr1":"value",...}
    """
    return PDMHandler.__get_attrs_by_list(tblnode,PDMHandler.TBL_ATTR_LIST)
  @staticmethod
  def getColAttrs(colnode):
    """
    @brief       获取指定o:Column的属性(可取的属性参见PDMHandler.COL_ATTR_LIST)
    @param[in]   colnode 待处理的o:Column节点(可通过PDMHandler.getColNodesInTbl取得)
    @return      返回一个字典dict:{"attr1":"value",...}
    """
    return PDMHandler.__get_attrs_by_list(colnode,PDMHandler.COL_ATTR_LIST)
  @staticmethod
  def getIdxAttrs(idxnode):
    """
    @brief       获取指定o:Index的属性(可取的属性参见PDMHandler.IDX_ATTR_LIST)
    @param[in]   idxnode 待处理的o:Index节点(可通过PDMHandler.getIdxNodesInTbl取得)
    @return      返回一个字典dict:{"attr1":"value",...}
    """
    return PDMHandler.__get_attrs_by_list(idxnode,PDMHandler.IDX_ATTR_LIST)
  @staticmethod
  def getIdxColAttrs(idxcolnode):
    """
    @brief       获取指定o:IndexColumn的属性(可取的属性参见PDMHandler.IDXCOL_ATTR_LIST)
    @param[in]   idxcolnode 待处理的o:IndexColumn节点(可通过PDMHandler.getIdxColNodesInIdx取得)
    @return      返回一个字典dict:{"attr1":"value",...}
    """
    ret_dict = PDMHandler.__get_attrs_by_list(idxcolnode,PDMHandler.IDXCOL_ATTR_LIST)
    refcol   = PDMHandler.__get_nodes_by_path(idxcolnode,"c:Column/o:Column")
    try:
      refcolid = refcol[0].getAttribute("Ref")
    except IndexError :
      ret_dict["RefColCode"] = ""
      return ret_dict
    #-- 补充引用列插入字典 --#
    currnode = idxcolnode
    while(1) :
      currnode = currnode.parentNode
      if currnode.tagName == "o:Table" or currnode == None :
        break
    if currnode == None :
      return []
    else :
      for col in PDMHandler.getColNodesInTbl(currnode) :
        if col.getAttribute("Id") == refcolid :
          ret_dict["RefColCode"] = PDMHandler.getColAttrs(col)["Code"]
    return ret_dict
  @staticmethod
  def getNodePath(node) :
    """
    @brief       获取指定node的路径(模拟文件系统路径表示法)
    @param[in]   node 待处理的节点,类型为DOM的节点类型
    @return      返回一个字符串表示node的路径,形如"/foo/bar/node"
    """
    curr = node
    path_nodes = []
    while(1):
      if curr != None and curr.nodeName != "#document" :
        path_nodes.append(curr.tagName)
      else :
        break
      curr = curr.parentNode 
    path_nodes.reverse()
    path = "".join([ slash + node for slash in '/' for node in path_nodes ])
    return path

  @staticmethod 
  def checkRules(tblnode) :
    """
    @获取符合架构处要求的sql形式
    """
    ins_flag = True
    ope_flag = True
    tbl_attrs = PDMHandler.getTblAttrs(tblnode)
    for col in PDMHandler.getColNodesInTbl(tblnode) :
      col_attrs = PDMHandler.getColAttrs(col)		 
      if col_attrs["Code"].upper()=="INSERTTIMEFORHIS":
        ins_flag = False
      if col_attrs["Code"].upper()=="OPERATETIMEFORHIS":
        ope_flag = False		  
        """if(col_attrs["Name"] == col_attrs["Code"]) :"""
      zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
      match = zhPattern.search(col_attrs["Name"])
      if match is None:
        """print ("  C:", col_attrs["Name"],col_attrs["Code"],col_attrs["DataType"],col_attrs["Length"],col_attrs["Column.Mandatory"])"""
        print ("< COMMENT ON COLUMN " ,tbl_attrs["Code"],".",col_attrs["Code"]," IS '" ,col_attrs["Code"],",",col_attrs["Comment"],"';>",sep='',file=f)
      if col_attrs["DataType"] =="VARCHAR2(1)":
        print ("< ALTER TABLE " ,tbl_attrs["Code"]," MODIFY (",col_attrs["Code"]," VARCHAR2(2));>",sep='',file=f)
    if ins_flag:
      print ("< ALTER TABLE " ,tbl_attrs["Code"]," ADD (INSERTTIMEFORHIS date);>",sep='',file=f)
      print ("< COMMENT ON COLUMN " ,tbl_attrs["Code"],".INSERTTIMEFORHIS IS 'INSERTTIMEFORHIS,插入时间_I';>",sep='',file=f)
    if ope_flag:
      print ("< ALTER TABLE " ,tbl_attrs["Code"]," ADD (OPERATETIMEFORHIS date);>",sep='',file=f)
      print ("< COMMENT ON COLUMN " ,tbl_attrs["Code"],".OPERATETIMEFORHIS IS 'OPERATETIMEFORHIS,更新时间_U';>",sep='',file=f)
    return
  @staticmethod 
  def checkRulesComment(tblnode) :
    """
    @获取符合架构处要求的sql形式
    """
    ins_flag = True
    ope_flag = True
    tbl_attrs = PDMHandler.getTblAttrs(tblnode)
    for col in PDMHandler.getColNodesInTbl(tblnode) :
      col_attrs = PDMHandler.getColAttrs(col)		 
      if col_attrs["Code"].upper()=="INSERTTIMEFORHIS":
        ins_flag = False
      if col_attrs["Code"].upper()=="OPERATETIMEFORHIS":
        ope_flag = False		  
        """if(col_attrs["Name"] == col_attrs["Code"]) :"""
      zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
      match = zhPattern.search(col_attrs["Name"])
      if match is None:
        """print ("  C:", col_attrs["Name"],col_attrs["Code"],col_attrs["DataType"],col_attrs["Length"],col_attrs["Column.Mandatory"])"""
        print (" COMMENT ON COLUMN " ,tbl_attrs["Code"],".",col_attrs["Code"]," IS '" ,col_attrs["Code"],",",col_attrs["Comment"],"';",sep='',file=f)
      """if col_attrs["DataType"] =="VARCHAR2(1)":
        print (" ALTER TABLE " ,tbl_attrs["Code"]," MODIFY (",col_attrs["Code"]," VARCHAR2(2));",sep='',file=f)
    if ins_flag:
      print (" ALTER TABLE " ,tbl_attrs["Code"]," ADD (INSERTTIMEFORHIS date);",sep='',file=f)
      print (" COMMENT ON COLUMN " ,tbl_attrs["Code"],".INSERTTIMEFORHIS IS 'INSERTTIMEFORHIS,插入时间_I';",sep='',file=f)
    if ope_flag:
      print (" ALTER TABLE " ,tbl_attrs["Code"]," ADD (OPERATETIMEFORHIS date);",sep='',file=f)
      print (" COMMENT ON COLUMN " ,tbl_attrs["Code"],".OPERATETIMEFORHIS IS 'OPERATETIMEFORHIS,更新时间_U';",sep='',file=f)"""
    return
""" 比较col中的name和code是否相同，如不同，则生成对应的修改comment语句。
如： comment on column table_code.col_code  IS col_code+","+""+";"
"""

if __name__ == '__main__' :
  import imp
  import re
  import string
  import sys
  imp.reload(sys)
  """sys.setdefaultencoding("utf-8")"""
  if len(sys.argv) <= 1:
    print ("USAGE:   ",sys.argv[0],"<filename>")
    print ("EXAMPLE: ",sys.argv[0],"data/Consol.pdm")
    sys.exit(1)
  else:
    filename = sys.argv[2]
  ph = PDMHandler.parse(filename)
  filename = sys.argv[1]
  ph_base = PDMHandler.parse(filename)
  f = open (r'E:\TestCenter\pythonScript\pdm.sql','w')
  print("delete table  doing....")
  for pkg_base in PDMHandler.getPkgNodes(ph_base):
    for tb_base in PDMHandler.getTblNodesInPkg(pkg_base):
      del_flag = True
      for pkg in PDMHandler.getPkgNodes(ph):
        for tbl in PDMHandler.getTblNodesInPkg(pkg):
          tbl_attrs = PDMHandler.getTblAttrs(tbl)
          tb_base_attrs = PDMHandler.getTblAttrs(tb_base)
          if tb_base_attrs["Code"] == tbl_attrs["Code"]:
            drop_str=""
            for col_base in PDMHandler.getColNodesInTbl(tb_base):
              col_base_attrs = PDMHandler.getColAttrs(col_base)
              drop_flag = True
              for col in PDMHandler.getColNodesInTbl(tbl) :
                col_attrs = PDMHandler.getColAttrs(col)
                if col_base_attrs["Code"]==col_attrs["Code"]:
                  drop_flag = False
                  break
              if drop_flag:
                drop_str=drop_str+''.join(col_base_attrs["Code"])+" "+''.join(col_base_attrs["DataType"])+"," 
            if drop_str!="":
              print("ALTER TABLE ",tbl_attrs["Code"], " DROP (",drop_str[:-1].upper(),");",sep='',file=f)
              """PDMHandler.checkRules(tbl)"""
            del_flag = False  
            break
      if del_flag:
        print (" DROP TABLE " ,tb_base_attrs["Code"]," ;",sep='',file=f)
  print("delete table  Done!!")
  print("create table  doing....")
  for pkg in PDMHandler.getPkgNodes(ph):
    for tbl in PDMHandler.getTblNodesInPkg(pkg):
      create_flag = True
      for pkg_base in PDMHandler.getPkgNodes(ph_base):
        for tb_base in PDMHandler.getTblNodesInPkg(pkg_base): 
          tbl_attrs = PDMHandler.getTblAttrs(tbl)
          tb_base_attrs = PDMHandler.getTblAttrs(tb_base)
          if tb_base_attrs["Code"] == tbl_attrs["Code"]:
            modify_str=""
            insert_str=""
            for col in PDMHandler.getColNodesInTbl(tbl) :
              insert_flag = True
              col_attrs = PDMHandler.getColAttrs(col)		              
              for col_base in PDMHandler.getColNodesInTbl(tb_base):
                col_base_attrs = PDMHandler.getColAttrs(col_base)
                if col_base_attrs["Code"]==col_attrs["Code"]:
                  insert_flag = False
                  if col_base_attrs["DataType"]!=col_attrs["DataType"]:
                    modify_str=modify_str+''.join(col_attrs["Code"])+" "+''.join(col_attrs["DataType"])+","
              if insert_flag:
                insert_str=insert_str+''.join(col_attrs["Code"])+" "+''.join(col_attrs["DataType"])+","
            if modify_str!="":
              print (modify_str)
              str1=''.join(modify_str)
              print("ALTER TABLE ",tbl_attrs["Code"], " MODIFY (",modify_str[:-1].upper(),");",sep='',file=f)
            if insert_str!="":
              print("ALTER TABLE ",tbl_attrs["Code"], " ADD (",insert_str[:-1].upper(),");",sep='',file=f)
            if(modify_str!="" or insert_str!=""):
              """PDMHandler.checkRules(tbl)"""				  
            create_flag = False  
            break
      if create_flag:
        print (" CREATE TABLE " ,tbl_attrs["Code"]," (",sep='',file=f)
        for col in PDMHandler.getColNodesInTbl(tbl) :
          col_attrs = PDMHandler.getColAttrs(col)
          print (col_attrs["Code"]," ",col_attrs["DataType"],",",sep='',file=f)
        print (");",sep='',file=f)
        PDMHandler.checkRules(tbl)
  print("create table  Done!!")
  f.close()
  f = open (r'E:\TestCenter\pythonScript\YXXT.sql','w')
  for pkg in PDMHandler.getPkgNodes(ph):
    for tbl in PDMHandler.getTblNodesInPkg(pkg):
      PDMHandler.checkRules(tbl)
  f.close() 
  print("check all the rules  Done!!")
  f = open (r'E:\TestCenter\pythonScript\YXXTComment.sql','w')
  for pkg in PDMHandler.getPkgNodes(ph):
    for tbl in PDMHandler.getTblNodesInPkg(pkg):
      PDMHandler.checkRulesComment(tbl)
  f.close()      
  print("check comment rules  Done!!")