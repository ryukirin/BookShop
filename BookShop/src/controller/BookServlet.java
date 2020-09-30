package controller;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import Service.CustomerDao;
import Service.MyDao;

@SuppressWarnings("serial")
@WebServlet("/jsp/book.action")

public class BookServlet extends HttpServlet {
	private CustomerDao dao = new CustomerDao();
	private MyDao mdao = new MyDao();
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		String opttype=request.getParameter("opttype");
		String bname,tname,bid,uid;
		switch(opttype){
		case "queryAllbook":
		    request.getSession().setAttribute("tlist", dao.queryAlltag());
		    request.getSession().setAttribute("blist", dao.queryAllbook());
			response.sendRedirect("buy.jsp");
		    break;
		case "queryByname":
			bname = request.getParameter("bname");
		    request.getSession().setAttribute("tlist", dao.queryAlltag());
			request.getSession().setAttribute("blist", dao.queryByName(bname));
			response.sendRedirect("buy.jsp");
		    break;
		case "queryBytag":
			tname=request.getParameter("tname");
		    request.getSession().setAttribute("tlist", dao.queryAlltag());
			request.getSession().setAttribute("blist", dao.queryByTag(tname));
			response.sendRedirect("buy.jsp");
		    break;
		case "bookDetail":
		    bid=request.getParameter("bid");
		    System.out.println(bid);
		    request.getSession().setAttribute("sblist", dao.showBook(bid));
		    System.out.println(dao.showBook(bid).toString());
			response.sendRedirect("bookdetails.jsp");
		    break;
		case "buybook":
			uid = (String)request.getSession().getAttribute("uid");
		    bid=request.getParameter("bid");
		    System.out.println(bid);
		    if(mdao.buyBook(bid,uid)>0)
				response.sendRedirect("my.action?opttype=queryMyorder");
		    break;
		}
	}

	
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
			doGet(request, response);
	}
}