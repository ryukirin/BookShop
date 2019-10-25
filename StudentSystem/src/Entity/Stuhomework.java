package Entity;

public class Stuhomework {
	public Stuhomework(String sname, String hname, String img, String cname) {
		super();
		this.sname = sname;
		this.hname = hname;
		this.img = img;
		this.cname = cname;
	}
	String sname;
	String hname;
	String img;
	String cname;
	public Stuhomework() {
		// TODO Auto-generated constructor stub
	}
	public String getSname() {
		return sname;
	}
	public void setSname(String sname) {
		this.sname = sname;
	}
	public String getHname() {
		return hname;
	}
	public void setHname(String hname) {
		this.hname = hname;
	}
	public String getImg() {
		return img;
	}
	public void setImg(String img) {
		this.img = img;
	}
	public String getCname() {
		return cname;
	}
	public void setCname(String cname) {
		this.cname = cname;
	}

}
