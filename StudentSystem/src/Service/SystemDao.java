package Service;

import java.util.ArrayList;
import java.util.List;

import Entity.*;
import dbutil.SQLHelper;

public class SystemDao {
	public String checkUsers(String uid, String upwd){
		String id = null;
		String pwd = upwd;
		String sql = "select pwd from user where uid='"+uid+"'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		System.out.println("select");
		if(!dblist.isEmpty()) {
			String  p = null;
			for(Object[] arr:dblist)
				p = arr[0].toString();
			if(p.equals(pwd))
				id = uid;
		}
		return id;
	}
	public String checkRoles(String uid){
		String role = null;
		String sql = "select rid from userrole where uid='"+uid+"'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		System.out.println("select");
		if(!dblist.isEmpty()) {
			for(Object[] arr:dblist)
				role = arr[0].toString();
		}
		return role;
	}
	public List<Note> queryAllnote(){
		List<Note> nlist = new ArrayList<Note>();
		String sql = "select aname, nid, nname, url, time\r\n" + 
				"from notes, admin\r\n" + 
				"where notes.aid = admin.aid\r\n" + 
				"order by time DESC\r\n"
				+ "limit 4;";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Note note = new Note();
			note.setAname(arr[0].toString());
			note.setNid(arr[1].toString());
			note.setNname(arr[2].toString());
			note.setUrl(arr[3].toString());
			note.setTime(arr[4].toString());
			nlist.add(note);
		}
		return nlist;
	}
	public int updatePwd(String pwd, String uid){
		String sql = "UPDATE user SET pwd='"+pwd+"' where uid='"+uid+"'";
		return SQLHelper.executeUpdate(sql);
	}
	public String checkPwd(String uid){
		String sql = "select pwd from user where uid='"+uid+"'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		String  pwd = null;
		for(Object[] arr:dblist)
			pwd = arr[0].toString();
		return pwd;
	}
	public int addBlog(Blog blog, String uid) {
		String sql1 = "INSERT INTO `student`.`blog` (`bname`, `url`, `uid`, `img`) VALUES (?, ?, ?, ?);";
		SQLHelper.executeUpdateByParams(sql1,blog.getBname(),blog.getUrl(),uid,blog.getImg());
		
		String sql2 = "select tid from tag where tname='"+blog.getTname()+"';";
		System.out.println(blog.getTname());
		List<Object[]> dblist1=SQLHelper.executeQueryList(sql2);
		String  t = null;
		for(Object[] arr:dblist1)
			t = arr[0].toString();
		String sql4 = "select bid from blog where uid = '"+uid+"' and bid not in (select bid from tbrelation where uid='"+uid+"');";
		List<Object[]> dblist2=SQLHelper.executeQueryList(sql4);
		for(Object[] arr:dblist2)
			blog.setBid(arr[0].toString());
		
		String sql3 = "INSERT INTO `student`.`tbrelation` (`bid`, `tid`, `uid`) VALUES (?, ?, ?);";
		return SQLHelper.executeUpdateByParams(sql3,blog.getBid(),t,uid);
	}
	public int addBlogimg(String img, String bid) {
		String sql = "update blog set img='"+img+"' where bid='"+bid+"';";
		return SQLHelper.executeUpdateByParams(sql);
	}
	
}
