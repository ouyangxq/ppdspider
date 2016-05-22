set names gbk;
create database ppdai;
use ppdai;

# for all Loan related information
create table ppdloan (
     loanid integer not null primary key,
     date date not null,
     ppdrate char(3) not null,
     loanrate FLOAT(4,2) not null,
     money integer not null,
     maturity integer not null,
     userid char(15) not null,
     loantitle varchar(30),
     age integer not null,
     history_return_ontime integer not null,
     history_overdue_in15d integer not null,
     history_overdue_mt15d integer not null,
     history_total_loan integer not null,
     history_left_loan double(10,2) not null,
     history_left_lend double(10,2) not null
);
alter table ppdloan add column datetime datetime not null;
alter table ppdloan add column has_30or36rate_loan_history BOOLEAN DEFAULT FALSE;
alter table ppdloan add column has_lt1000_loan_history BOOLEAN DEFAULT FALSE; 
alter table ppdloan add column new_total_loan double(10,2);
alter table ppdloan add column history_highest_total_loan double(10,2);
alter tbale ppdloan add column source char(20) DEFAULT 'page_walker';

# User information
create table ppduser (
     userid char(15) not null primary key,
     gender varchar(4) not null,
     age int not null,
     marriage varchar(4),
     house varchar(10),
     car varchar(5),
     education_level varchar(10),
     education_university varchar(20) DEFAULT NULL,
     education_type varchar(10) DEFAULT NULL,
     ren_hang_trust_cert BOOLEAN DEFAULT FALSE,
     idcard_cert BOOLEAN DEFAULT FALSE,
     hukou_cert BOOLEAN DEFAULT FALSE,
     alipay_cert BOOLEAN DEFAULT FALSE,
     job_cert BOOLEAN DEFAULT FALSE,
     shebao_gjj_cert BOOLEAN DEFAULT FALSE,
     bank_details_cert BOOLEAN DEFAULT FALSE,
     taobao_seller_cert BOOLEAN DEFAULT FALSE,
     relative_cert BOOLEAN DEFAULT FALSE,
     shouru_cert BOOLEAN DEFAULT FALSE
)          
alter table ppduser add column mobile_cert BOOLEAN DEFAULT FALSE;
# Test
insert into ppduser values ('pdu2517', 'male', 34, 'married', 'yes', 'no', 'master', 'xidian', 'normal', 0, 1, 0, 0,0,0,0,0,0)     

# My Bid records
# All loan related information are in ppdloan table
create table mybid (
	loanid integer not null,
	datetime datetime not null,
	money integer not null,
	reason varchar(180) not null,
	ppduserid char(15) not null,
	byautobid boolean not null default 0,
	primary key (loanid,ppduserid)
);
alter table mybid add column strategy_name char(30) DEFAULT NULL;

create table bidstrategy (
	strategy_name char(30) primary key NOT NULL;
	strategy_criteria char(250) NOT NULL;
);

alter table mybid add column strategy_criteria char(30) DEFAULT NULL;

create table university (
	name varchar(25) not null primary key,
	rank int,
	score float(4,2),
	type varchar(8) not null,
	location varchar (8) not null,
	pici varchar (10) not null
);

create table blacklist (
	id integer not null auto_increment,
	loanid integer not null,
	ppbaouserid char(15) not null,
	loanuserid char(15) not null,
	loantitle varchar(40) not null,
	returned_money FLOAT(4,2) not null,
	overdue_money FLOAT(4,2) not null,
	bid_money integer not null,
	overdue_days integer not null,
	history_max_overdue_days integer not null,
	overdue_date date not null,
	return_date date default NULL,
	primary key (id)
);

create table myprofit (
    date date not null,
    ppbaouserid char(15) not null,
    realized_profits FLOAT(4,2) not null,
    unrealized_profits FLOAT(4,2) not null,
    blacklist_count int not null,
    blacklist_bid_money int not null,
    blacklist_returned_money FLOAT(4,2) not null,
    blacklist_overdue_money FLOAT(4,2) not null,
    max_loss_money FLOAT(4,2) not null,
    min_profits FLOAT(4,2) not null,
    primary key (date,ppbaouserid)
);