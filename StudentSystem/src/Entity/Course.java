package Entity;

public class Course {
	private String cno;
	private String cname;
	private String cla;//∑÷¿‡
	private String tname;
	private String num;
	private String cont;//ºÚΩÈ
	public Course(String cno, String cname, String cla, String tname, String num, String cont) {
		super();
		this.cno = cno;
		this.cname = cname;
		this.cla = cla;
		this.tname = tname;
		this.num = num;
		this.cont = cont;
	}
	public Course() {
		super();
	}
	public String getCno() {
		return cno;
	}
	public void setCno(String cno) {
		this.cno = cno;
	}
	public String getCname() {
		return cname;
	}
	public void setCname(String cname) {
		this.cname = cname;
	}
	public String getCla() {
		return cla;
	}
	public void setCla(String cla) {
		this.cla = cla;
	}
	public String getTname() {
		return tname;
	}
	public void setTname(String tname) {
		this.tname = tname;
	}
	public String getNum() {
		return num;
	}
	public void setNum(String num) {
		this.num = num;
	}
	public String getCont() {
		return cont;
	}
	public void setCont(String cont) {
		this.cont = cont;
	}
}
