package controller;
 
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.Date;

import javax.servlet.ServletException;
import javax.servlet.ServletOutputStream;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import Service.MyDao;
 
@WebServlet("/jsp/DownLoadServlet")
public class DownloadServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
	MyDao dao = new MyDao();
    public DownloadServlet() {
        super();
    }
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doPost(request,response);
	}
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		String filename,hid;
        hid=request.getParameter("hid");
		filename = dao.queryMygbook(hid);
		//实现文件下载 设置响应头
		String fileName = this.getServletContext().getRealPath("")+"..\\"+"download\\"+filename;
		filename = new Date().getTime()+(int)(Math.random()*100)+filename;
		response.setHeader("Content-Disposition", "attachment;filename="+filename);
		System .out.print("fileName"+fileName);
		//先使用文件输入流 将文件读到内存中 再使用输出流 将文件输出给用户
		File file = new File(fileName);
		FileInputStream fileIn = new FileInputStream(file);
		//准备一个缓冲区
		byte[] b = new byte[(int)file.length()];
		//将文件读入缓冲区中
		fileIn.read(b);
		//获得响应的输出流
		ServletOutputStream sout = response.getOutputStream();
//调用response.getOutputStream()方法返回 ServeltOutputStream 对象来向客户端写入文件内容。
		sout.write(b);
		sout.close();
	}
}