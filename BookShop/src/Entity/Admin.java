package Entity;

public class Admin extends Users {
	private String aid;
	private String aname;
	public Admin(String id, String aname) {
		super();
		this.aid = id;
		this.aname = aname;
	}
	public Admin() {
		super();
	}
	public String getAid() {
		return aid;
	}
	public void setAid(String aid) {
		this.aid = aid;
	}
	public String getAname() {
		return aname;
	}
	public void setAname(String aname) {
		this.aname = aname;
	}
}
