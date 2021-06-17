from math import pi
from random import Random
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union,
)

from pydantic import (
    Field,
    PrivateAttr,
    validator,
)

from .plugin import GeneratorBase
from .random import SeedStore


class RandomGeneratorBase(GeneratorBase):
    _random: Random = PrivateAttr()

    def setup(self, seed_store: SeedStore):
        self._random = Random(seed_store.next())


class RandomBeta(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.beta"

    alpha: float = Field(..., description="The alpha value for the distribution")
    beta: float = Field(..., description="The beta value for the distribution")

    def generate(self) -> float:
        return self._random.betavariate(self.alpha, self.beta)


class RandomChoice(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.choice"

    choices: List[Any] = Field(
        ..., description="Sequence of elements to randomly choose from"
    )

    def generate(self) -> Any:
        return self._random.choice(self.choices)

    @validator("choices")
    def choices_must_be_non_empty(cls, v: List[Any]):
        assert len(v) > 0, "Choices must contain at least one element"
        return v


class RandomChoices(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.choices"

    choices: List[Any] = Field(
        ..., description="Sequence of elements to randomly choose from"
    )

    weights: Optional[List[Union[float, int]]] = Field(
        None, description="Weights of the elements"
    )
    cum_weights: Optional[List[Union[float, int]]] = Field(
        None, description="Cumulative weights of the elements"
    )
    size: int = Field(1, description="The number of elements to be chosen")

    def generate(self) -> List[Any]:
        return self._random.choices(
            population=self.choices,
            weights=self.weights,
            cum_weights=self.cum_weights,
            k=self.size,
        )

    @validator("choices")
    def choices_must_be_non_empty(cls, v: List[Any]):
        assert len(v) > 0, "Choices must contain at least one element"
        return v

    @validator("cum_weights")
    def weights_exclusivity(cls, v: List[Any], values: Dict[str, Any]):
        assert (
            values["weights"] is None
        ), "Cannot define weights and cumulative weights at the same time"
        return v


class RandomExponential(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.exponential"

    lambda_: float = Field(
        ..., description="The lambda parameter for the distribution", alias="lambda"
    )

    def generate(self) -> float:
        return self._random.expovariate(self.lambda_)

    @validator("lambda_")
    def non_zero_lambda(cls, v: float):
        assert v != 0, "Lambda must not be zero"
        return v


class RandomGamma(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.gamma"

    alpha: float = Field(..., description="The alpha value for the distribution")
    beta: float = Field(..., description="The beta value for the distribution")

    def generate(self) -> float:
        return self._random.gammavariate(self.alpha, self.beta)

    @validator("alpha", "beta")
    def greater_than_zero(cls, v: float):
        assert v > 0, "Distribution parameters must be > 0"
        return v


class RandomGauss(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.gauss"

    mu: float = Field(..., description="The mu value for the distribution")
    sigma: float = Field(..., description="The sigma value for the distribution")

    def generate(self) -> float:
        return self._random.gauss(self.mu, self.sigma)

    @validator("sigma")
    def non_negative_sigma(cls, v: float):
        assert v > 0, "Sigma must be greater than 0"
        return v


class RandomBits(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.bits"

    bits: int = Field(..., description="The number of bits to randomly generate")

    def generate(self) -> int:
        return self._random.getrandbits(self.bits)

    @validator("bits")
    def non_zero_bits(cls, v: int):
        assert v > 0, "Bits must be greater than 0"
        return v


class RandomLogNormal(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.log_normal"

    mu: float = Field(..., description="The mu value for the distribution")
    sigma: float = Field(..., description="The sigma value for the distribution")

    def generate(self) -> float:
        return self._random.lognormvariate(self.mu, self.sigma)

    @validator("sigma")
    def non_negative_sigma(cls, v: float):
        assert v >= 0, "Sigma must not be negative"
        return v


class RandomNormal(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.normal"

    mu: float = Field(..., description="The mu value for the distribution")
    sigma: float = Field(..., description="The sigma value for the distribution")

    def generate(self) -> float:
        return self._random.normalvariate(self.mu, self.sigma)

    @validator("sigma")
    def non_negative_sigma(cls, v: float):
        assert v >= 0, "Sigma must not be negative"
        return v


class RandomPareto(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.pareto"

    alpha: float = Field(..., description="The alpha value for the distribution")

    def generate(self) -> float:
        return self._random.paretovariate(self.alpha)

    @validator("alpha")
    def non_zero_alpha(cls, v: float):
        assert v != 0, "Alpha must not be zero 0"
        return v


class RandomInt(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.int"
    min_: int = Field(..., description="The lower bound", alias="min")
    max_: int = Field(..., description="The upper bound", alias="max")

    def generate(self) -> int:
        return self._random.randint(self.min_, self.max_)


class RandomRange(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.range"
    start: int = Field(..., description="The start of random range")
    stop: Optional[int] = Field(
        ..., description="The optional stop for the random range"
    )
    step: int = Field(1, description="The step between range elements")

    def generate(self) -> int:
        return self._random.randrange(self.start, self.stop, self.step)


class RandomRandom(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.random"

    def generate(self) -> float:
        return self._random.random()


class RandomSample(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.sample"

    choices: List[Any] = Field(..., description="The elements to sample from")
    size: int = Field(1, description="The number of elements to sample")

    def generate(self) -> List[Any]:
        return self._random.sample(self.choices, self.size)

    @validator("size")
    def non_negative_size(cls, v: int):
        assert v >= 0, "Size must not be negative"
        return v

    @validator("size")
    def non_size_max_len_choices(cls, v: int, values: Dict[str, Any]):
        if "choices" in values:
            assert v <= len(
                values["choices"]
            ), "Sample size can't exceed number of available choices"
        return v


class RandomTriangular(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.triangular"

    low: float = Field(..., description="The low value for the distribution")
    high: float = Field(..., description="The high value for the distribution")
    mode: float = Field(..., description="The mode value for the distribution")

    def generate(self) -> float:
        return self._random.triangular(self.low, self.high, self.mode)


class RandomUniform(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.uniform"

    a: float = Field(..., description="The start of the range for the distribution")
    b: float = Field(..., description="The end of the range for the distribution")

    def generate(self) -> float:
        return self._random.uniform(self.a, self.b)


class RandomVonMises(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.von_mises"

    mu: float = Field(..., description="The mu value for the distribution")
    kappa: float = Field(..., description="The kappa value for the distribution")

    def generate(self) -> float:
        return self._random.vonmisesvariate(self.mu, self.kappa)

    @validator("mu")
    def mu_value_range(cls, v: float):
        assert v >= 0 and v <= 2 * pi, "Mu must be of form 0 <= mu <= 2*pi"
        return

    @validator("kappa")
    def non_negative_kappa(cls, v: int):
        assert v >= 0, "Kappa must not be negative"
        return v


class RandomWeibull(RandomGeneratorBase):
    yaml_tag: ClassVar[str] = u"!random.weibull"

    alpha: float = Field(..., description="The alpha value for the distribution")
    beta: float = Field(..., description="The beta value for the distribution")

    def generate(self) -> float:
        return self._random.weibullvariate(self.alpha, self.beta)

    @validator("beta")
    def non_zero_beta(cls, v: float):
        assert v != 0, "beta must not be zero 0"
        return v
