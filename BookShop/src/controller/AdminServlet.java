package controller;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.fileupload.FileItem;
import org.apache.commons.fileupload.FileUploadException;
import org.apache.commons.fileupload.disk.DiskFileItemFactory;
import org.apache.commons.fileupload.servlet.ServletFileUpload;

import Entity.Book;
import Service.AdminDao;

@SuppressWarnings("serial")
@WebServlet("/jsp/admin.action")
public class AdminServlet extends HttpServlet {
	private AdminDao dao=new AdminDao();
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		String opttype=request.getParameter("opttype");
		String bid, uid, bname, publishers, stock, price, tname, url = null, cont,uname;
		switch(opttype){
		case "queryAllcustomers":
			 request.getSession().setAttribute("clist", dao.queryCustomer());
			 response.sendRedirect("admin.jsp");
		    break;
		case "queryCustomers":
			uname=request.getParameter("uname");
			request.getSession().setAttribute("clist", dao.queryUserByUname(uname));
			response.sendRedirect("admin.jsp");
		    break;
		case "deleteCustomers":
		    uid=request.getParameter("uid");
		    if(dao.deleteCustomerById(uid)>0)
				response.sendRedirect("admin.action?opttype=queryAllcustomers");
		    break;
		case "queryAllbooks":
			 request.getSession().setAttribute("blist", dao.queryAllbook());
			 response.sendRedirect("bookadmin.jsp");
		    break;
		case "queryBooks":
			bname=request.getParameter("bname");
			request.getSession().setAttribute("blist", dao.queryBookByname(bname));
			response.sendRedirect("bookadmin.jsp");
		    break;
		case "addBooks":
			request.setCharacterEncoding("utf-8");
			bname = request.getParameter("bname");
			request.getSession().setAttribute("bname", bname);
			request.setCharacterEncoding("utf-8");
			publishers = request.getParameter("publishers");
			request.getSession().setAttribute("publishers", publishers);
			request.setCharacterEncoding("utf-8");
			stock = request.getParameter("stock");
			request.getSession().setAttribute("stock", stock);
			request.setCharacterEncoding("utf-8");
			price = request.getParameter("price");
			request.getSession().setAttribute("price", price);
			request.setCharacterEncoding("utf-8");
			tname = request.getParameter("tname");
			request.getSession().setAttribute("tname", tname);
			request.setCharacterEncoding("utf-8");
			cont = request.getParameter("cont");
			request.getSession().setAttribute("cont", cont);
			System.out.println(bname+publishers+cont+stock+price+tname);
			response.sendRedirect("addnext.jsp?bname="+bname+"&publishers="+publishers+
					"&stock="+stock+"&price="+price+"&tname="+tname+"&cont="+cont+"");
		    break;
		case "addBooksimg":
			request.setCharacterEncoding("utf-8");
			bname = (String)request.getSession().getAttribute("bname");
			request.setCharacterEncoding("utf-8");
			publishers = (String)request.getSession().getAttribute("publishers");
			request.setCharacterEncoding("utf-8");
			stock = (String)request.getSession().getAttribute("stock");
			request.setCharacterEncoding("utf-8");
			price = (String)request.getSession().getAttribute("price");
			request.setCharacterEncoding("utf-8");
			tname = (String)request.getSession().getAttribute("tname");
			request.setCharacterEncoding("utf-8");
			cont = (String)request.getSession().getAttribute("cont");
			request.setAttribute("message", "");
			request.setAttribute("url", "");
			String filename = null;
			// 设置上传图片的保存路径
			String savePath = this.getServletContext().getRealPath("/img");
			File file = new File(savePath);
			DiskFileItemFactory factory = new DiskFileItemFactory();
			// 2、创建一个文件上传解析器
			ServletFileUpload upload = new ServletFileUpload(factory);
			upload.setHeaderEncoding("UTF-8");
			// 3、判断提交上来的数据是否是上传表单的数据
			if (!ServletFileUpload.isMultipartContent(request)) {
				// 按照传统方式获取数据
				return;
			}
			try {
				List<FileItem> list = upload.parseRequest(request);
				System.out.println(list.toString());// 文件的路径 以及保存的路径
				for (FileItem item : list) {
					 filename = System.currentTimeMillis()+item.getName();// 获得一个项的文件名称
					if (filename == null || filename.trim().equals("")) {// 如果為空則跳過
						continue;
					}
	 
					filename = filename.substring(filename.lastIndexOf("\\") + 1);
//					System.out.print(filename);
					if (filename.substring(filename.lastIndexOf(".") + 1).equals("png")
							|| filename.substring(filename.lastIndexOf(".") + 1).equals("jpg")
							|| filename.substring(filename.lastIndexOf(".") + 1).equals("jpeg")) {
						InputStream in = item.getInputStream();// 獲得上傳的輸入流
						FileOutputStream out = new FileOutputStream(savePath + "\\" + filename);// 指定web-inf目錄下的images文件
						request.getSession().setAttribute("url", filename);
	 
						int len = 0;
						byte buffer[] = new byte[1024];
						while ((len = in.read(buffer)) > 0)// 每次讀取
						{
							out.write(buffer, 0, len);
						}
						in.close();
						out.close();
						item.delete();
					} else {  //必须是图片才能上传否则失败
						return ;
					}
				}
			} catch (FileUploadException e) {
				e.printStackTrace();
			}
			request.setAttribute("message", "上传成功");
			request.setCharacterEncoding("gbk");
			url = (String)request.getSession().getAttribute("url");
			System.out.println(bname+publishers+cont+stock+price+tname+url);
			Book book = new Book(bname, publishers, cont, stock, price, tname, url);
		    if(dao.addBook(book)>0)
				response.sendRedirect("admin.action?opttype=queryAllbooks");
			break;
		case "showBooks":
			bid=request.getParameter("bid");
			request.getSession().setAttribute("eblist", dao.queryBookByid(bid));
			System.out.println(dao.queryBookByid(bid).toString());
			response.sendRedirect("editbook.jsp");
			break;
		case "editBooks":
			bid = request.getParameter("bid");
			publishers = request.getParameter("publishers");
			stock = request.getParameter("stock");
			price = request.getParameter("price");
			System.out.println(bid+publishers+stock+price);
		    if(dao.updateBook(bid, stock, publishers, price)>0)
				response.sendRedirect("admin.action?opttype=queryAllbooks");
		    break;
		case "deleteBooks":
			bid=request.getParameter("bid");
		    if(dao.deleteBookById(bid)>0)
				response.sendRedirect("admin.action?opttype=queryAllbooks");
		    break;
		case "showAllmoney":
			request.getSession().setAttribute("olist", dao.queryAllorder());
			request.getSession().setAttribute("sum", dao.sumPrice());
			response.sendRedirect("oderadmin.jsp");
		    break;
		}
	}

	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request, response);
	}

}
