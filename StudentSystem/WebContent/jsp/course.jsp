<%@ page language="java" pageEncoding="utf-8"%> 
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>课程</title>
<link rel="stylesheet" type="text/css" href="../css/course.css"></link>

</head>
 
<body>
<div class="header" id="head">
  <div class="title">你好！</div>
  <div class="tab">
		  <ul>
		  	<li class="selected">
		  		<a href="course.action?opttype=queryAllcourse">课程</a>
		  	</li>
		  	<li>
		  		<a href="blog.action?opttype=queryAllblog">博客</a>
		  	</li>
		  	<li>
		  		<a href="my.action?opttype=initMypage">个人</a>
		  	</li>
		  </ul>
	</div>
	<form class="search" action='course.action' type="post">
		<input type=hidden name="opttype" value="queryByname" />
		<input type="text" name="cname" placeholder="请输入关键字">
		<button id="search" type="submit">搜索</button>
	</form>
</div>
<div class="wrap" id="wrap">
	<div id="leftbar">
		<table class="lefttable">
			<tr>
				<th>所有分类<hr></hr></th>
			</tr>
			<c:forEach var="t" items="${tlist}">
		    	<tr>
		    	   <th><a  href='course.action?opttype=queryBycla&cla=${t.cla}'>${t.cla}</a><hr></hr></th>
		 		</tr>
		 	</c:forEach>
		</table>
	</div>
	<div id="main">
		<form>
			<table >
			<c:forEach var="c" items="${clist}">
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