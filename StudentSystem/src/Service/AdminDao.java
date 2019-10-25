package Service;

import java.util.ArrayList;
import java.util.List;

import Entity.*;
import dbutil.SQLHelper;

public class AdminDao {
	public Users queryUserById(String uid) {
		Users user = null;
		String sql = "select user.uid, uname, rid from user, userrole where user.uid='"+uid+"' and user.uid = userrole.uid";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		if(dblist.size()>0){
		    user = new Users();
		    Object[] arr=dblist.get(0);
			user.setId(arr[0].toString());
			user.setName(arr[1].toString());
			user.setRole(arr[2].toString());
		}		
		return user;
	}
	public List<Users> queryUsers() {
		List<Users> ulist = new ArrayList<Users>();
		String sql = "select user.uid, uname, rid from user, userrole where user.uid = userrole.uid";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		for(Object[] arr:dblist){
			Users user=new Users();
			user.setId(arr[0].toString());
			user.setName(arr[1].toString());
			user.setRole(arr[2].toString());
			ulist.add(user);
		}
		return ulist;
	}
	public int updateUsers(String uid,String name,String role) {
		String sql = "update user set uname='"+name+"' where uid='"+uid+"';";
		SQLHelper.executeUpdate(sql);
		String sql1 = "update userrole set rid='"+role+"' where uid='"+uid+"';";
		return SQLHelper.executeUpdate(sql1);
	    
	}
	public int addUsers(Users user) {
		String sql = "INSERT INTO user (`uid`, `uname`) VALUES ('"+user.getId()+"','"+user.getName()+"');";
		SQLHelper.executeUpdate(sql);
		String sql1 = "INSERT INTO userrole (`rid`, `uid`) VALUES ('"+user.getRole()+"', '"+user.getId()+"');";
		return SQLHelper.executeUpdate(sql1);
	}

	public int deleteUsersById(String uid) {
		String sql = "delete from userrole where  uid=?;";
		SQLHelper.executeUpdateByParams(sql,uid);
		String sql1 = "delete from user where  uid=?;";
		return SQLHelper.executeUpdateByParams(sql1,uid);
	}
}
