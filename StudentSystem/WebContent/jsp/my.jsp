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

    <title>购买</title>

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
          <a class="navbar-brand" href="../index.jsp">网上药店</a>
        </div>
        <div id="navbar" class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li><a href="../index.jsp">主页</a></li>
            <li><a href="buy.jsp">购买</a></li>
            <li><a href="want.jsp">购物车</a></li>
            <li><a href="msg.jsp">留言</a></li>
            <li class="active"><a href="my.jsp">个人</a></li>
          </ul>
        </div><!-- /.nav-collapse -->
      </div><!-- /.container -->
    </nav><!-- /.navbar -->

    <div class="container-fluid">
      <div class="row">
        <div class="col-sm-3 col-md-2 sidebar">
          <ul class="nav nav-sidebar">
            <li class="active"><a href="#">个人信息 <span class="sr-only">(current)</span></a></li>
            <li><a href="#">修改密码</a></li>
						<li><a href="#">我的订单</a></li>
            <li><a href="#">我的健康</a></li>
          </ul>
        </div>
        <div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
          <h1 class="page-header">个人信息</h1>

          <div class="row placeholders">
            <div class="col-xs-6 col-sm-3 placeholder">
              <img src="data:image/gif;base64,R0lGODlhAQABAIAAAHd3dwAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw==" width="130" height="130" class="img-responsive" alt="Generic placeholder thumbnail">
              <h4>用户名</h4>
              <span class="text-muted">女</span>
            </div>
          </div>

          <h2 class="sub-header">地址</h2>
          <div class="table-responsive">
           <a href="addr.jsp"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> 添加</a>
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>地址</th>
                  <th>手机</th>
                  <th>收货人</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>上海市浦东新区南汇新城镇沪城环路1851号上海电力大学</td>
                  <td>1111111111111111111</td>
                  <td>L</td>
                  <td><a><span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>
									修改</a>
									<a><span class="glyphicon glyphicon-trash" aria-hidden="true"></span>
									删除</a></td>
                </tr>
                 <tr>
                   <td>上海市浦东新区南汇新城镇沪城环路1851号上海电力大学</td>
                   <td>1111111111111111111</td>
                   <td>L</td>
                   <td><a><span class="glyphicon glyphicon-pencil" aria-hidden="true"></span>
                 	修改</a>
                 	<a><span class="glyphicon glyphicon-trash" aria-hidden="true"></span>
                 	删除</a></td>
                 </tr>
								 <tr>
								   <td>上海市浦东新区南汇新城镇沪城环路1851号上海电力大学</td>
								   <td>1111111111111111111</td>
								   <td>L</td>
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
