package Entity;

public class Users {
	private String uid;
	private String name;
	private String pwd;
	private String role;
	public Users() {
		super();
	}
	public Users(String uid, String name, String pwd, String role) {
		this.uid = uid;
		this.name = name;
		this.pwd = pwd;
		this.role = role;
	}
	public Users(String name, String pwd, String role) {
		this.pwd = pwd;
		this.name = name;
		this.role = role;
	}
	public String getUid() {
		return uid;
	}
	public void setUid(String uid) {
		this.uid = uid;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getPwd() {
		return pwd;
	}
	public void setPwd(String pwd) {
		this.pwd = pwd;
	}
	public String getRole() {
		return role;
	}
	public void setRole(String role) {
		this.role = role;
	}
}
