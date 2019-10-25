<%@ page language="java" pageEncoding="utf-8"%> 
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>个人</title>
<link rel="stylesheet" type="text/css" href="../css/my.css"></link>
<script type="text/javascript">
  function clock(){
  var time=new Date();
  var week;
  switch (time.getDay()){            <!--time.getDay()获取后显示1~7阿拉伯数字 -->
    case 1: week="星期一"; break;
    case 2: week="星期二"; break;
    case 3: week="星期三"; break;
    case 4: week="星期四"; break;
    case 5: week="星期五"; break;
    case 6: week="星期六"; break;
    default: week="星期天";
  }
	var year=time.getFullYear();
	var month=time.getMonth();
	var date=time.getDate();
        document.getElementById("clock").innerHTML = "&nbsp今天是："+year+"年"+(month+1)+"月"+date+"日  "+week;
	document.getElementById("footyear").innerHTML = year;
  }
  setInterval(clock,1000);     <!--每隔1秒显示一次-->
</script>
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
		<div class="page">
			<h1 class="date" id="clock"></h1>
			<div class="mycourse">
				<h3>&nbsp;&nbsp;我的课程</h3>
				<table class="coursedetail">
					<tr>
						<c:forEach var="c" items="${mlist}">
							<td><hr size="200" width="0" color="whitesmoke"></td>
							<td width="480px">
								<h2><a href="course.action?opttype=courseDetail&cno=${c.cno}">${c.cname }</a></h2>
								<h5><a  href='course.action?opttype=queryBytea&tname=${c.tname}'>${c.tname}</a></h5>
								<h6>上课人数：${c.num }</h6></br>
								<h5 class="context">${c.cont }</h5>
							</td>
							<td><hr size="200" width="1"></td>
					 	</c:forEach>
					 </tr>
				</table>
				<div class="more">
					<a href="my.action?opttype=queryMycourse">more></a>
				</div>
			</div>
			<hr class="myhr" />
			<div class="notice">
				<table class="noticetext">
					<tr>
						<h4 class="tablename" align="center">公告栏</h4>
					</tr>
					<c:forEach var="c" items="${nlist}">
						<tr>
							<td>${c.time }&nbsp|&nbsp${c.nname}<hr /></td>
						</tr>
					</c:forEach>
					<tr>
						<td><a class="morenotice" href="#">more></a><hr /></td>
					</tr>
				</table>
			</div>
		</div>
	</div>
</div>
	
</body>
</html>