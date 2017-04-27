function CalcObject= sleepcalc2(file,n,t)
%Calculates the sleep frequency(sfreq),sleep total duration (stdur),
%sleep/30min (s30) and mean sleep duration (smdur)
% arguments 
%file=data file Ej. o01
%n=sleep definition
%t=time interval for the sfreq, stdur and smdur

% On 2-9-10 changed output to CalcObject from the following:
% [amean,sfreq,stdur,s30,smedian,smax,smeandur,oamean,atcounts,namean,ameandur,afreq,atdur,latency,MeanWakeningsDur,wmax,WSdiff]


m=file.f;
[x y]= size(m);
for j=1:y                   
    for i=1:(x/30)          
        amean(i,j)=nanmean(m((1+(i-1)*30):i*30,j));
    end
end

Z=fly_histo(file);
B=(Z>=n);

[x y]= size(B);
for j=1:y                   
    for i=1:(x/t)          
        sfreq(i,j)=sum(B((1+(i-1)*t):i*t,j));
    end
end

Z2=fly_acthisto(file,n);
B=Z2>0;

[x y]= size(B);
for j=1:y                   
    for i=1:(x/t)          
        afreq(i,j)=sum(B((1+(i-1)*t):i*t,j));
    end
end


H=Z;
[x,y]=size(H);
for i=1:x
    for j=1:y
       if H(i,j)<n
       H(i,j)=NaN;
       end
    end
end

[x y]= size(H);
for j=1:y                   
    for i=1:(x/t)          
        smedian2(i,j)=nanmedian(H((1+(i-1)*t):i*t,j));
    end
end
smedian=smedian2;
smedian(find(isnan(smedian)))=0;

[x y]= size(H);
for j=1:y                   
    for i=1:(x/t)          
        smeandur2(i,j)=nanmean(H((1+(i-1)*t):i*t,j));
    end
end
smeandur=smeandur2;
smeandur(find(isnan(smeandur)))=0;

[x y]= size(Z2);
for j=1:y                   
    for i=1:(x/t)          
        ameandur2(i,j)=nanmean(Z2((1+(i-1)*t):i*t,j));
    end
end

ameandur=ameandur2;
ameandur(find(isnan(ameandur)))=0;

[x y]= size(H);
for j=1:y                   
    for i=1:(x/t)          
        smax2(i,j)=nanmax(H((1+(i-1)*t):i*t,j));
    end
end

smax=smax2;
smax(find(isnan(smax)))=0;

Z2=fly_acthisto(file,n);
B2=Z2>0;

[x y]= size(B2);
for j=1:y                   
    for i=1:(x/t)          
        wmax(i,j)=nanmax(Z2((1+(i-1)*t):i*t,j));
    end
end

wmax(find(isnan(wmax)))=0;

WSdiff=wmax-smax;

[a,s30]=fly_sleepthresh(file,n);

[x y]= size(a);
for j=1:y                    
    for i=1:(x/t)           
        stdur(i,j)=sum(a((1+(i-1)*t):i*t,j));
    end
end

[a,s30]=fly_sleepthresh(file,n);
a2=a<1;
[x y]= size(a2);
for j=1:y                    
    for i=1:(x/t)           
        atdur(i,j)=sum(a2((1+(i-1)*t):i*t,j));
    end
end

b=file.f;

[x,y]=size(b);
for i=1:x
    for j=1:y
       if b(i,j)==0;
       b(i,j)=NaN;
   else H(i,j)=1;
       end
    end
end

[x y]= size(b);
for j=1:y                   
    for i=1:(x/t)          
        namean(i,j)=nanmean(b((1+(i-1)*t):i*t,j));
    end
end


[a,s30]=fly_sleepthresh(file,n);
H=a;
[x,y]=size(H);
for i=1:x
    for j=1:y
        if H(i,j)==1;
            H(i,j)=NaN;
        else H(i,j)=1;
        end
    end
end

b=file.f.*H;

[x y]= size(b);
for j=1:y                   
    for i=1:(x/t)          
        oamean2(i,j)=nanmean(b((1+(i-1)*t):i*t,j));
    end
end
oamean=oamean2;
oamean(find(isnan(oamean)))=0;

b=file.f;

[x y]= size(b);
for j=1:y                   
    for i=1:(x/t)          
        atcounts(i,j)=nansum(b((1+(i-1)*t):i*t,j));
    end
end

% New Material 2-9-10 - Added fset_v2, which outputs latency,...
% added MeanWakeDur, which outputs MeanWakeningsDur
% Then added CalcObject, function of which is to lump all sleepcalc2 data
% into a single cell object

% fset_v2

[C,s30]=fly_sleepthresh(file,n);   
[x y]= size(C);
for j=1:y                   
    for i=1:(x/t)  
        try
        [latency(i,j)]=find(C((1+(i-1)*t):i*t,j),1,'first');
        catch
        latency(i,j)=t;
        end
    end 
end

% MeanWakeDur_v2

TotTimeActive=t-stdur;

wakeningsDur=TotTimeActive-(latency-1);

MeanWakeningsDur=wakeningsDur./afreq;

MeanWakeningsDur(find(isnan(MeanWakeningsDur)))=0;
MeanWakeningsDur(find(isinf(MeanWakeningsDur)))=0;
MeanWakeningsDur;

% CalcObject

CalcObject={amean,s30,stdur,sfreq,smax,smeandur,smedian,oamean,atcounts,...
    namean,ameandur,afreq,atdur,latency,MeanWakeningsDur};
