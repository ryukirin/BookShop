<%@ page language="java" pageEncoding="utf-8"%> 
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>我的课程</title>
<link rel="stylesheet" type="text/css" href="../css/mycourse.css"></link>
<link rel="stylesheet" type="text/css" href="../css/course.css"></link>

</head>
 
<body>
<div class="header" id="head">
  <div class="title">你好！</div>
  <div class="tab">
		  <ul>
		  	<li>
		  		<a href="course.action?opttype=queryAllcourse">课程</a>
		  	</li>
		  	<li>
		  		<a href="blog.action?opttype=queryAllblog">博客</a>
		  	</li>
		  	<li class="selected">
		  		<a href="my.action?opttype=initMypage">个人</a>
		  	</li>
		  </ul>
	</div>
</div>
<div class="wrap" id="wrap">
	<div id="leftbar">
		<table class="lefttable">
			<tr>
				<th><a href="teachagepwd.jsp">修改密码</a><hr></hr></th>
			</tr>
			<tr>
				<th><a href="my.action?opttype=queryMycourse">我的课程</a><hr></hr></th>
			</tr>
			<tr>
				<th><a href="my.action?opttype=queryMyblog">我的博客</a><hr></hr></th>
			</tr>
			<tr>
				<th><a href="#">申请开班</a><hr></hr></th>
			</tr>
		</table>
	</div>
	<div id="main">
		<form>
			<table >
			<c:forEach var="c" items="${mlist}">
				<tr>
					<th>
						<div class="course">
							<table class="coursedetail">
								<tr>
									<td>
										<h2><a href="course.action?opttype=courseDetail&cno=${c.cno}">${c.cname }</a></h2>
										<h5><a  href='course.action?opttype=queryBytea&tname=${c.tname}'>${c.tname}</a></h5>
										<h6>上课人数：${c.num }</h6></br>
										<h5 class="context">${c.cont }</h5>
									</td>
								</tr>
							</table>
						</div>
					</th>
				</tr>
		 	</c:forEach>
			</table>
		</form>
	</div>
</div>

</body>
</html>