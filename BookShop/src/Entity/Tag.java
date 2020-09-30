package Entity;

public class Tag {
	private String tid;
	private String tname;
	public Tag(String tid, String tname) {
		super();
		this.tid = tid;
		this.tname = tname;
	}
	public Tag() {
		super();
	}
	public String getTid() {
		return tid;
	}
	public void setTid(String tid) {
		this.tid =tid;
	}
	public String getTname() {
		return tname;
	}
	public void setTname(String tname) {
		this.tname = tname;
	}
}
