dat= read.csv("~/Downloads/T8-svar/za_dat.csv")
y <- ts(log(dat$RGDP[-1]), start = c(1990, 2), freq = 4)  # output
pi <- ts(diff(log(dat$CPI)) * 100, start = c(1990, 2), freq = 4)  # consumer inflation
i.tmp <- (1 + (dat$repo/100))^0.25 - 1  # annualised interest rates
i <- ts(i.tmp[-1] * 100, start = c(1990, 2), freq = 4)

data <- cbind(y, pi, i)
colnames(data) <- c("y", "pi", "i")

p = 3
y = as.matrix(data)
orig_y = y
type = "const"
n_obs = dim(y)[1]
k = dim(y)[2]
sample = n_obs - p
ylags = embed(y, dimension = p + 1)[, -(1:k)]
temp1 = NULL # ylags column names
for (i in 1:p) {
  temp <- paste(colnames(y), ".l", i, sep = "")
  temp1 <- c(temp1, temp)
}
colnames(ylags) = temp1
yend = y[-c(1:p), ]
# Constant
rhs = cbind(ylags, rep(1, sample))
colnames(rhs) <- c(colnames(ylags), "const")


datamat <- as.data.frame(rhs)
colnames(datamat) <- colnames(rhs)
equation <- list()
for (i in 1:k) {
  y <- yend[, i]
  equation[[colnames(yend)[i]]] <- lm(y ~ -1 + ., data = datamat)
  if(any(c("const", "both") %in% type)){
    attr(equation[[colnames(yend)[i]]]$terms, "intercept") <- 1
  }
}

Y = t(yend)
X = t(rhs)
coefs = (Y%*%t(X))%*%solve(X%*%t(X))
epsilon = Y - coefs%*%X
cov = epsilon%*%t(epsilon) / (n_obs - p -p*k -1)
