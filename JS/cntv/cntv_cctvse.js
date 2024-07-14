// 无搜索功能
import { _ } from './lib/cat.js';
let key = '视聚场';
let HOST = 'http://api.cntv.cn';
let siteKey = '';
let siteType = 0;
const MOBILE_UA = 'Mozilla/5.0 (Linux; Android 11; M2007J3SC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36';

async function request(reqUrl, agentSp) {
    let res = await req(reqUrl, {
        method: 'get',
        headers: {
            'User-Agent': agentSp || MOBILE_UA,
        },
    });
    return res.content
}

async function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype
}

async function home(filter) {
    const classes = [ 
{ type_name: "新闻袋袋裤" , type_id: "TOPC1451559603261584" },
{ type_name: "英雄出少年" , type_id: "TOPC1451559695702690" },
{ type_name: "七巧板" , type_id: "TOPC1451559569040502" },
{ type_name: "快乐体验" , type_id: "TOPC1451559479171411" },
{ type_name: "智力快车" , type_id: "TOPC1451559756374759" },
{ type_name: "动感特区" , type_id: "TOPC1451559378830189" },
{ type_name: "音乐快递" , type_id: "TOPC1451559666055645" },
{ type_name: "SK极智少年强" , type_id: "TOPC1476950587121943" },
{ type_name: "加油！少年派" , type_id: "TOPC1451464548229761" },
{ type_name: "风车剧场" , type_id: "TOPC1573528152700717" },
{ type_name: "希望-英语杂志" , type_id: "TOPC1451558013229330" },
{ type_name: "成长在线" , type_id: "TOPC1451559901017891" },
{ type_name: "童心回放" , type_id: "TOPC1451559966897957" },
{ type_name: "文学宝库" , type_id: "TOPC1451560002205989" },
{ type_name: "大仓库" , type_id: "TOPC1451559344361150" },
{ type_name: "宝贝一家亲" , type_id: "TOPC1451559867985861" },
{ type_name: "绿野寻踪" , type_id: "TOPC1451559534065469" },
{ type_name: "芝麻开门" , type_id: "TOPC1451559725520729" },
{ type_name: "异想天开" , type_id: "TOPC1451559633994614" }
        ];
    const filterObj = {};
    return JSON.stringify({
        class: _.map(classes, (cls) => {
            cls.land = 1;
            cls.ratio = 1.78;
            return cls;
        }),
        filters: filterObj,
    })
}

async function homeVod() {
    const data = JSON.parse(await request(HOST + '/NewVideo/getVideoListByColumn?id=TOPC1451558856402351&n=10&sort=desc&p=1&mode=0&serviceId=tvcctv'));
    let videos = _.map(data.data.list, (it) => {
        return {
            vod_id: it.guid,
            vod_name: it.title,
            vod_pic: it.image,
            vod_remarks: it.time || '',
        }
    });
    return JSON.stringify({
        list: videos,
    })
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0 || typeof pg == 'undefined') pg = 1;
    const data = JSON.parse(await request(HOST + '/NewVideo/getVideoListByColumn?id=' + tid + '&n=10&sort=desc&p=' + pg + '&mode=0&serviceId=tvcctv'));
    let videos = _.map(data.data.list, (it) => {
        return {
            vod_id: it.guid,
            vod_name: it.title,
            vod_pic: it.image,
            vod_remarks: it.time || '',
        }
    });
    const pgChk = JSON.parse(await request(HOST + '/NewVideo/getVideoListByColumn?id=' + tid + '&n=10&sort=desc&p=' + (parseInt(pg) + 1) + '&mode=0&serviceId=tvcctv')).data.list;
    const pgCount = pgChk.length > 0 ? parseInt(pg) + 1 : parseInt(pg);
    return JSON.stringify({
        page: parseInt(pg),
        pagecount: parseInt(pgCount),
        limit: 10,
        total: parseInt(data.total),
        list: videos,
    })
}

async function detail(id) {
    const vod = {
        vod_id: id,
        vod_remarks: '',
    };
    const playlist = ['点击播放' + '$' + 'https://hls.cntv.myhwcdn.cn/asp/hls/2000/0303000a/3/default/' + id + '/2000.m3u8'];
    vod.vod_play_from = key;
    vod.vod_play_url = playlist.join('#');
    return JSON.stringify({
        list: [vod],
    });
}

async function play(flag, id, flags) {
    // console.debug('视聚场 id =====>' + id); // js_debug.log
    return JSON.stringify({
        parse: 0,
        url: id,
    })
}

async function search(wd, quick, pg) {
    return '{}'
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        detail: detail,
        play: play,
        search: search,
    }
}