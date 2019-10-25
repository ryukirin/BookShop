<%@ page language="java" import="java.util.*" pageEncoding="utf-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
	<head>
		<script type="text/javascript" src="ckeditor/ckeditor.js"></script>
		<script type="text/javascript" src="ckeditor/ckeditor_msg.js"></script>  
		<script type="text/javascript">
			//<![CDATA[   
			CKEDITOR.replace('content', {
				toolbar : 'Full',
				skin : 'kama'
			});
			//]]>  
			function save() {
				//JavaScript判空，如果确定
				var editor_data = CKEDITOR.instances.content.getData();
				if(editor_data==null||editor_data==""){
					alert("数据为空不能提交");
				}else{
					if(confirm(editor_data)){
					document.myform.submit();
					}
				}		
			}
		</script>
		<title>写博客</title>
		<link rel="stylesheet" type="text/css" href="../css/wirte.css"></link>
	</head>
	<body>
	<form action="user.action" name="myform" method="get">
	<input type=hidden name="opttype" value="add" />
		<table class="wirtetable">
			<tr>
				<td> 
					标题：<input class="blogtitle" name="bname" type="text" />
					
				</td>
			</tr>
			<tr>
				<td> 
					标签：<select name="tname">        <!--下拉列表框-->
					<c:forEach var="c" items="${tlist}">
						<option value="${c.tname }">${c.tname }</option>
		 			</c:forEach>
					</select>
				</td>
			</tr>
			<tr>
				<td>
					<textarea class="ckeditor" cols="80" id="content" name="content" rows="10"></textarea>
					<button class="save" type="submit" onclick="save()" value='提交'>提交</button>
     			</td>
			</tr>
		</table>
     </form>
	</body>
</html>