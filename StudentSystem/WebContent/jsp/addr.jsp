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
          <h1 class="page-header">添加地址</h1>
          <div class="table-responsive">
						<form class="form-signin" onsubmit="window.location.href = 'addnext.jsp'">
							<label for="aname" class="sr-only">收货人</label>
							<input type="text" id="aname" class="form-control" placeholder="收货人" required autofocus>
						</br>
						<label for="atel" class="sr-only">收货电话</label>
							<input type="text" id="atel" class="form-control" placeholder="收货电话" required autofocus>
						</br><label for="ahome" class="sr-only">收货地址</label>
							<input type="text" id="ahome" class="form-control" placeholder="收货地址，XX省XX市XX街道" required autofocus>
						</br><button type="submit" class="btn btn-success">创建</button>
						</form>
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
