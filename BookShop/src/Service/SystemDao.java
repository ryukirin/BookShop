package Service;

import java.util.List;

import dbutil.SQLHelper;

public class SystemDao {
	/**
	 * check user's password right or not
	 * @param uid,pwd
	 * @return id
	 */
	public String checkUsers(String uid, String upwd){
		String id = null;
		String pwd = upwd;
		String  p = null;
		String sql = "select upwd from user where uid='"+uid+"'";
		System.out.println(sql);
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		if(!dblist.isEmpty()) {
			for(Object[] arr:dblist)
				p = arr[0].toString();
			if(p.equals(pwd))
				id = uid;
		}
		return id;
	}
	/**
	 * check user's password
	 * @param uid
	 * @return pwd
	 */
	public String checkPwd(String uid){
		String sql = "select upwd from user where uid='"+uid+"'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		String  pwd = null;
		for(Object[] arr:dblist)
			pwd = arr[0].toString();
		return pwd;
	}
	/**
	 * check user's role,1 is customer,2 is admin
	 * @param uid
	 * @return role
	 */
	public String checkRoles(String uid){
		String role = null;
		String sql = "select role from book.user where uid = '"+uid+"'";
		List<Object[]> dblist=SQLHelper.executeQueryList(sql);
		if(!dblist.isEmpty()) {
			for(Object[] arr:dblist)
				role = arr[0].toString();
		}
		return role;
	}
}
