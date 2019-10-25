package Entity;

public class Blog {
	private String bid;
	private String bname;
	private String url;
	private String uname;
	private String cnum;
	private String img;
	private String eva;
	private String tname;
	public Blog(String bid, String bname, String url, String uname, String cnum, String img, String eva, String tname) {
		super();
		this.bid = bid;
		this.bname = bname;
		this.url = url;
		this.uname = uname;
		this.cnum = cnum;
		this.img = img;
		this.eva = eva;
		this.tname = tname;
	}
	public Blog(String bname, String url, String tname) {
		super();
		this.bname = bname;
		this.url = url;
		this.tname = tname;
	}
	public Blog(String bname, String url, String tname,String img) {
		super();
		this.bname = bname;
		this.url = url;
		this.tname = tname;
		this.img = img;
	}
	public Blog() {
		super();
	}
	public String getBid() {
		return bid;
	}
	public void setBid(String bid) {
		this.bid = bid;
	}
	public String getBname() {
		return bname;
	}
	public void setBname(String bname) {
		this.bname = bname;
	}
	public String getUrl() {
		return url;
	}
	public void setUrl(String url) {
		this.url = url;
	}
	public String getUname() {
		return uname;
	}
	public void setUname(String uname) {
		this.uname = uname;
	}
	public String getCnum() {
		return cnum;
	}
	public void setCnum(String cnum) {
		this.cnum = cnum;
	}
	public String getEva() {
		return eva;
	}
	public void setEva(String eva) {
		this.eva = eva;
	}
	public String getTname() {
		return tname;
	}
	public void setTname(String tname) {
		this.tname = tname;
	}
	public String getImg() {
		return img;
	}
	public void setImg(String img) {
		this.img = img;
	}
}
