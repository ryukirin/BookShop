<%@ page language="java" import="Service.AdminDao,Entity.Users" pageEncoding="utf-8"%>
<!DOCTYPE html>
<html>
	<head>
	  <title>编辑用户</title>
	 
	</head>
	<body>
	 
	  <form name="frm1" action="admin.action" method="get">
	    <input type=hidden name="opttype" value="update" />
			    用户id:<input type=text name="uid" value="${c.id }" readonly><br/>
			    用户名:<input type=text name="name" value="${c.name }"><br/>
			    用户角色:
						<select name="role">
							<option value="1"  selected>学生</option>	
							<option value="2">老师</option>
							<option value="3" >管理员</option>	
						</select>
					</td><br/>
	     <input type=submit value="更改">
	  </form> 
	</body>
</html>