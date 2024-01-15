package com.github.catvod.spider;


import android.text.TextUtils;

import com.github.catvod.bean.Class;
import com.github.catvod.bean.Filter;
import com.github.catvod.bean.Result;
import com.github.catvod.bean.Vod;
import com.github.catvod.crawler.Spider;
import com.github.catvod.net.OkHttp;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Mimiju extends Spider {

    private final String url = "https://mimiju.com/";

    @Override
    public String homeContent(boolean filter) throws Exception {

        List<Vod> list = new ArrayList<>();
        List<Class> classes = new ArrayList<>();
        LinkedHashMap<String,List<Filter>> filters = new LinkedHashMap<>();
        Document doc = Jsoup.parse(OkHttp.string(url + "vodtype/20.html"));
        List<String> typeIds = Arrays.asList("20","21","22","23","24");
        for(Element a:doc.select("ul.hl-nav > li.hl-nav-item > a")) {
            String typeId = a.attr("href").replace(url,"");
            if(!typeIds.contains(typeId)) continue;
            classes.add(new Class(typeId, a.text()));
            List<Filter.Value> filterValues = new ArrayList<>();
            filterValues.add(new Filter.Value("全部", ""));
            filterValues.add(new Filter.Value("短剧", "20.html"));
            filterValues.add(new Filter.Value("电视剧", "21.html"));
            List<Filter> filterList = new ArrayList<>();
            filterList.add(new Filter("filters", "过滤", filterValues));
            filters.put(typeId, filterList);
        }

        for(Element div : doc.select("li.hl-list-item")) {
            String id = div.select("a.hl-item-thumb").attr("href").replace(url,"");
            String name = div.select("a.hl-item-thumb").attr("title");
            String pic = "https://mimiju.com/" +  div.select("a.hl-item-thumb").attr("data-original");
            String remark = div.select("span.hl-lc-1 .remarks").text();
            if(TextUtils.isEmpty(name)) continue;
            list.add(new Vod(id, name, pic, remark));
        }
        return Result.string(classes, list, filters);
    }

    @Override
    public String categoryContent(String tid, String pg, boolean filter, HashMap<String, String> extend) throws Exception {
        List<Vod> list = new ArrayList<>();
        String target = url + "vodtype/" + tid + ".html";
        String filters = extend.get("filters");
        if(TextUtils.isEmpty(filters)) target = target + "-" + pg + "html";
        else target = target + "-" + pg + "html" +"?filters=" + extend.get("filters");
        Document doc = Jsoup.parse(OkHttp.string(target));
        for(Element div : doc.select("li.hl-list-item")) {
            String id = div.select("a.hl-item-thumb").attr("href").replace(url,"");
            String name = div.select("a").attr("title");
            String pic = div.select("a").attr("data-original");
            String remark = div.select("span.hl-lc-1 .remarks").text();
            if(TextUtils.isEmpty(name)) continue;
            list.add(new Vod(id, name, pic, remark));
        }
        return Result.string(list);
    }

    @Override
    public String detailContent(List<String> ids) throws Exception {
        Document doc = Jsoup.parse(OkHttp.string(url.concat(ids.get(0))));
        String name = doc.select("h2.hl-dc-title").text();
        String remarks = doc.select("span.hl-text-conch").text();
        String img = doc.select("span.hl-item-thumb .hl-lazy").attr("data-original");
        Vod vod = new Vod();
        vod.setVodId(ids.get(0));
        vod.setVodPic(img);
        vod.setVodRemarks(remarks);
        vod.setVodName(name);

        Map<String,String> sites = new LinkedHashMap<>();
        Elements source = doc.select("div.hl-plays-from > a");
        Elements sourceList = doc.select("ul.hl-plays-list");
        for(int i=0; i<source.size();i++){
            Element element = source.get(i);
            String sourceName = element.text();
            Elements playList = sourceList.get(i).select("a");
            List<String> vodItems = new ArrayList<>();
            for(int j=0;j<playList.size();j++) {
                Element e = playList.get(j);
                vodItems.add(e.text() + "$" + e.attr("href"));
            }
            if(vodItems.size() > 0) {
                sites.put(sourceName, TextUtils.join("#", vodItems));
            }
        }
        if(sites.size() > 0){
            vod.setVodPlayFrom(TextUtils.join("$$$",sites.keySet()));
            vod.setVodPlayUrl(TextUtils.join("$$$",sites.values()));
        }
        return Result.string(vod);
    }

    @Override
    public String searchContent(String key, boolean quick) {
        List<Vod> list = new ArrayList<>();
        String target = url.concat("vodsearch/-------------.html?wd=").concat(key);
        Document doc = Jsoup.parse(OkHttp.string(target));
        for(Element element :doc.select("li.hl-list-item")) {
            String img = element.select("a.hl-item-thumb").attr("data-original");
            String url = element.select("a.hl-item-thumb").attr("href");
            String name = element.select("div.hl-item-title > a").text();
            String remark = element.select("span.hl-lc-1").text();
            list.add(new Vod(url, name, img, remark));
        }
        return Result.string(list);
    }

    @Override
    public String playerContent(String flag, String id, List<String> vipFlags) {
        Document doc = Jsoup.parse(OkHttp.string(url.concat(id)));
        String url = "https://mimiju.com" + doc.select("iframe").attr("src");
        return Result.get().url(url).parse().string();
    }
}

