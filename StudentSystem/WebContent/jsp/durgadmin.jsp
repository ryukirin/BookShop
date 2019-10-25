<%@ page language="java" pageEncoding="utf-8"%> 
<!doctype html>
<html>
<head>
	<meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="">
    <meta name="author" content="">

    <title>网上药店管理站</title>

    <!-- Bootstrap core CSS -->
    <link href="../bootstrap/docs/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <link href="../bootstrap/docs/assets/css/ie10-viewport-bug-workaround.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="../css/dashboard.css" rel="stylesheet">

    <!-- Just for debugging purposes. Don't actually copy these 2 lines! -->
    <!--[if lt IE 9]><script src="../../assets/js/ie8-responsive-file-warning.js"></script><![endif]-->
    <script src="../bootstrap/docs/assets/js/ie-emulation-modes-warning.js"></script>

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>

  <body>

    <nav class="navbar navbar-fixed-top navbar-inverse">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand">网上药店管理站</a>
          
          <form class="navbar-form navbar-right">
            <input type="text" class="form-control" placeholder="查询...">
          </form>
        </div>
      </div><!-- /.container -->
    </nav><!-- /.navbar -->

    <div class="container-fluid">
      <div class="row">
        <div class="col-sm-3 col-md-2 sidebar">
          <ul class="nav nav-sidebar">
            <li><a href="admin.jsp">会员管理 <span class="sr-only">(current)</span></a></li>
            <li class="active"><a href="durgadmin.jsp">药品管理</a></li>
			<li><a href="msgadmin.jsp">留言管理</a></li>
          </ul>
        </div>
        <div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
          <h1 class="page-header">药品管理</h1>
          <div class="table-responsive">
          <a href="add.jsp"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> 添加</a>
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>药品id</th>
                  <th>药品名</th>
                  <th>生产厂家</th>
                  <th>药品类型</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>00000001</td>
                  <td>三九</td>
                  <td>。。。</td>
                  <td>。。。</td>
                  <td><a><span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>
					修改</a>
					<a><span class="glyphicon glyphicon-trash" aria-hidden="true"></span>
					删除</a></td>
                </tr>
                 <tr>
                   <td>00000001</td>
                   <td>三九</td>
                  <td>。。。</td>
                   <td>。。。</td>
                   <td><a><span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>
                 	修改</a>
                 	<a><span class="glyphicon glyphicon-trash" aria-hidden="true"></span>
                 	删除</a></td>
                 </tr>
				<tr>
					<td>00000001</td>
					<td>三九</td>
                  <td>。。。</td>
					<td>。。。</td>
					<td><a><span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>
					修改</a>
					<a><span class="glyphicon glyphicon-trash" aria-hidden="true"></span>
					删除</a></td>
				</tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>



    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
    <script>window.jQuery || document.write('<script src="../bootstrap/docs/assets/js/vendor/jquery.min.js"><\/script>')</script>
    <script src="../bootstrap/docs//js/bootstrap.min.js"></script>
    <!-- Just to make our placeholder images work. Don't actually copy the next line! -->
    <script src="../bootstrap/docs//js/vendor/holder.min.js"></script>
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="../bootstrap/docs//js/ie10-viewport-bug-workaround.js"></script>
  </body>
</html>
