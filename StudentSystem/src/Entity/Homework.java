package Entity;

public class Homework {
	String hid;
	String hname;
	String gbook;
	String cname;
	public Homework(String hid, String hname,String gbook, String cname) {
		super();
		this.hid = hid;
		this.hname = hname;
		this.gbook = gbook;
		this.cname = cname;
	}
	public Homework() {
		super();
	}
	public String getHid() {
		return hid;
	}
	public void setHid(String hid) {
		this.hid = hid;
	}
	public String getHname() {
		return hname;
	}
	public void setHname(String hname) {
		this.hname = hname;
	}
	public String getCname() {
		return cname;
	}
	public void setCname(String cname) {
		this.cname = cname;
	}
	public String getGbook() {
		return gbook;
	}
	public void setGbook(String gbook) {
		this.gbook = gbook;
	}
}
