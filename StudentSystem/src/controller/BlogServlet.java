package controller;
import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import Service.StudentDao;

@SuppressWarnings("serial")
@WebServlet("/jsp/blog.action")

public class BlogServlet extends HttpServlet {
	private StudentDao dao = new StudentDao();
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		String opttype=request.getParameter("opttype");
		String tname,bname,uname,bid;
		switch(opttype){
		case "queryAllblog":
		    request.getSession().setAttribute("tlist", dao.queryAlltag());
		    request.getSession().setAttribute("blist", dao.queryAllblog());
			response.sendRedirect("blog.jsp");
		    break;
		case "queryBybname":
			bname = request.getParameter("bname");
		    request.getSession().setAttribute("tlist", dao.queryAlltag());
			request.getSession().setAttribute("blist", dao.queryByBname(bname));
			response.sendRedirect("blog.jsp");
		    break;
		case "queryBytag":
			tname=request.getParameter("tag");
		    request.getSession().setAttribute("tlist", dao.queryAlltag());
			request.getSession().setAttribute("blist", dao.queryByTag(tname));
			response.sendRedirect("blog.jsp");
		    break;
		case "queryByuser":
		    uname=request.getParameter("uname");
		    request.getSession().setAttribute("tlist", dao.queryAlltag());
		    request.getSession().setAttribute("blist", dao.queryByUser(uname));
			response.sendRedirect("blog.jsp");
		    break;
		case "blogDetail":
		    bid=request.getParameter("bid");
		    request.getSession().setAttribute("bdlist", dao.showBlog(bid));
			response.sendRedirect("blogdetail.jsp");
		    break;
		}
	}

	
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
			doGet(request, response);
	}
}
