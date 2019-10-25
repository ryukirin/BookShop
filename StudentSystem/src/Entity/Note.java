package Entity;

public class Note {
	private String nid;
	private String nname;
	private String url;
	private String aname;
	private String time;
	public Note() {
		super();
	}
	public Note(String nid, String nname, String url, String aname, String time) {
		super();
		this.nid = nid;
		this.nname = nname;
		this.url = url;
		this.aname = aname;
		this.time = time;
	}
	public String getNid() {
		return nid;
	}
	public void setNid(String nid) {
		this.nid = nid;
	}
	public String getNname() {
		return nname;
	}
	public void setNname(String nname) {
		this.nname = nname;
	}
	public String getUrl() {
		return url;
	}
	public void setUrl(String url) {
		this.url = url;
	}
	public String getAname() {
		return aname;
	}
	public void setAname(String aname) {
		this.aname = aname;
	}
	public String getTime() {
		return time;
	}
	public void setTime(String time) {
		this.time = time;
	}

}
