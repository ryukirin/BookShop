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

    <!-- Custom styles for this template 
    <link rel="stylesheet" type="text/css" href="../css/wirte.css"></link>-->
    <link href="../css/offcanvas.css" rel="stylesheet">

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
            <li class="active"><a href="msg.jsp">留言</a></li>
            <li><a href="my.jsp">个人</a></li>
          </ul>
        </div><!-- /.nav-collapse -->
      </div><!-- /.container -->
    </nav><!-- /.navbar -->

    <div class="container">
        <h1>留言板</h1>
		<div class="list-group">
			<a href="#" class="list-group-item">
				<h4 class="list-group-item-heading">用户名</h4>
				<p class="list-group-item-text">评论内容</p>
				<p class="list-group-item-text">2019/01/09</p>
			</a>
			<a href="#" class="list-group-item">
				<h4 class="list-group-item-heading">用户名</h4>
				<p class="list-group-item-text">评论内容</p>
				<p class="list-group-item-text">2019/01/09</p>
			</a>
			<a href="#" class="list-group-item">
				<h4 class="list-group-item-heading">用户名</h4>
				<p class="list-group-item-text">评论内容</p>
				<p class="list-group-item-text">2019/01/09</p>
			</a>
			<a href="#" class="list-group-item">
				<h4 class="list-group-item-heading">用户名</h4>
				<p class="list-group-item-text">评论内容</p>
				<p class="list-group-item-text">2019/01/09</p>
			</a>
			<a href="#" class="list-group-item">
				<h4 class="list-group-item-heading">用户名</h4>
				<p class="list-group-item-text">评论内容</p>
				<p class="list-group-item-text">2019/01/09</p>
			</a>
		</div>
		<div>
			<form role="form">
			  <div class="form-group">
			    <h4>留言</h4>
			    <textarea class="form-control" rows="3" required></textarea>
			    </br>
			    <button class="btn btn-primary" type="submit" onclick="save()" value='提交'>提交</button>
			  </div>
			</form>
		</div>
      

    </div><!--/.container-->


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
    <script>window.jQuery || document.write('<script src="../../assets/js/vendor/jquery.min.js"><\/script>')</script>
    <script src="../bootstrap/docs/dist/js/bootstrap.min.js"></script>
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="../bootstrap/docs/assets/js/ie10-viewport-bug-workaround.js"></script>
    <script src="offcanvas.js"></script>
  </body>
</html>